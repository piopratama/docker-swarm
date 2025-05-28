import asyncio
import asyncpg
import redis.asyncio as aioredis
import os
import uuid

async def consume():
    # Ambil config dari ENV atau fallback lokal
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 5433))
    DB_USER = os.getenv("DB_USER", "order")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "orderpass")
    DB_NAME = os.getenv("DB_NAME", "order_db")

    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

    # Koneksi DB dan Redis
    db_pool = await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST,
        port=DB_PORT,
    )

    redis = await aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}", decode_responses=True)

    # Stream config
    stream_key = "user_created"
    group = "order_group"
    consumer = "order_consumer"

    # Buat group kalau belum ada
    try:
        await redis.xgroup_create(stream_key, group, id="$", mkstream=True)
    except Exception:
        pass

    print("👂 Listening for events in Redis stream...")

    # Loop consume
    while True:
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
                        "INSERT INTO orders (id, user_id, product_name, total_price) VALUES ($1, $2, $3, $4)",
                        order_id, user_id, product, price
                    )

                await redis.xack(stream_key, group, msg_id)
                print(f"✅ Order created for user {user_id}")

if __name__ == "__main__":
    asyncio.run(consume())
