import asyncio
import asyncpg
import redis.asyncio as aioredis
import os
import uuid
import socket
import time
import signal

# Graceful shutdown event
stop_event = asyncio.Event()

def shutdown_handler(*args):
    print("🛑 Shutdown signal received. Exiting...")
    stop_event.set()

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

async def wait_for_service(connect_func, retries=5, delay=2):
    for i in range(retries):
        try:
            return await connect_func()
        except Exception as e:
            print(f"Retry {i+1}/{retries}: {e}")
            await asyncio.sleep(delay)
    raise Exception("Failed to connect after retries")

async def consume():
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 5433))
    DB_USER = os.getenv("DB_USER", "order")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "orderpass")
    DB_NAME = os.getenv("DB_NAME", "order_db")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

    async def connect_db():
        return await asyncpg.create_pool(
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            host=DB_HOST,
            port=DB_PORT,
        )

    async def connect_redis():
        return await aioredis.from_url(
            f"redis://{REDIS_HOST}:{REDIS_PORT}",
            decode_responses=True
        )

    db_pool = await wait_for_service(connect_db)
    redis = await wait_for_service(connect_redis)

    stream_key = "user_created"
    group = "order_group"
    consumer = f"consumer_{socket.gethostname()}"

    # Create group if it doesn't exist
    try:
        await redis.xgroup_create(stream_key, group, id="$", mkstream=True)
    except Exception:
        pass  # Likely already exists

    print(f"👂 {consumer} listening for events in Redis stream...")

    while not stop_event.is_set():
        try:
            messages = await redis.xreadgroup(
                groupname=group,
                consumername=consumer,
                streams={stream_key: ">"},
                count=1,
                block=5000
            )

            for stream, msgs in messages:
                for msg_id, data in msgs:
                    user_id = data["user_id"]
                    product = "Auto Order"
                    price = 50.0
                    order_id = str(uuid.uuid4())

                    async with db_pool.acquire() as conn:
                        await conn.execute(
                            """
                            INSERT INTO orders (id, user_id, product_name, total_price)
                            VALUES ($1, $2, $3, $4)
                            ON CONFLICT (id) DO NOTHING
                            """,
                            order_id, user_id, product, price
                        )

                    await redis.xack(stream_key, group, msg_id)
                    print(f"✅ {consumer}: Order created for user {user_id}")

        except Exception as e:
            print(f"⚠️ Error in stream processing: {e}")
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(consume())
