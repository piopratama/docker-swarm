import os
import uuid
import asyncio
import asyncpg
import redis.asyncio as aioredis
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS configuration (for frontend, Docker, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables with fallbacks
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5433))
DB_USER = os.getenv("DB_USER", "order")
DB_PASSWORD = os.getenv("DB_PASSWORD", "orderpass")
DB_NAME = os.getenv("DB_NAME", "order_db")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Global resources
db_pool = None
redis = None

# Retry wrapper for services
async def wait_for_service(connect_func, retries=5, delay=2):
    for i in range(retries):
        try:
            return await connect_func()
        except Exception as e:
            print(f"Retry {i+1}/{retries} - {e}")
            await asyncio.sleep(delay)
    raise Exception("Failed to connect after retries")

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

@app.on_event("startup")
async def startup():
    global db_pool, redis
    db_pool = await wait_for_service(connect_db)
    redis = await wait_for_service(connect_redis)
    print("✅ Connected to DB and Redis")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/order")
async def create_order(request: Request):
    body = await request.json()

    user_id = body.get("user_id", str(uuid.uuid4()))
    product = body.get("product", "Sample Product")
    price = body.get("price", 99.99)
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

    return {"message": "Order created", "id": order_id}

@app.get("/summary")
async def get_summary():
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT user_id, COUNT(*) AS total_orders, SUM(total_price) AS total_spent
            FROM orders
            GROUP BY user_id
            """
        )

    summary = [
        {
            "user_id": row["user_id"],
            "total_orders": row["total_orders"],
            "total_spent": float(row["total_spent"]),
        }
        for row in rows
    ]

    return {"summary": summary}
