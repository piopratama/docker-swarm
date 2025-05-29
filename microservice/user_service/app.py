import os
import uuid
import asyncio
import asyncpg
import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS untuk akses dari frontend lokal
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Untuk demo, izinkan semua origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variabel untuk koneksi
db_pool = None
redis = None

# Retry helper
async def wait_for_service(connect_func, retries=5, delay=2):
    for i in range(retries):
        try:
            return await connect_func()
        except Exception as e:
            print(f"Retry {i+1}/{retries} - {e}")
            await asyncio.sleep(delay)
    raise Exception("Failed to connect after retries")

@app.on_event("startup")
async def startup():
    global db_pool, redis

    db_host = os.getenv("DB_HOST", "localhost")
    redis_host = os.getenv("REDIS_HOST", "localhost")
    db_user = os.getenv("DB_USER", "user")
    db_password = os.getenv("DB_PASSWORD", "userpass")
    db_name = os.getenv("DB_NAME", "user_db")

    async def connect_db():
        return await asyncpg.create_pool(
            user=db_user,
            password=db_password,
            database=db_name,
            host=db_host,
            port=int(os.getenv("DB_PORT", 5432)),
        )

    async def connect_redis():
        return await aioredis.from_url(f"redis://{redis_host}", decode_responses=True)

    db_pool = await wait_for_service(connect_db)
    redis = await wait_for_service(connect_redis)

    print("✅ Connected to DB and Redis")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/user")
async def create_user():
    user_id = str(uuid.uuid4())
    name = "John Doe"
    email = "john@example.com"

    # Simpan ke database
    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO users (id, name, email)
            VALUES ($1, $2, $3)
            ON CONFLICT (id) DO NOTHING
            """,
            user_id, name, email
        )

    # Publish event ke Redis stream
    await redis.xadd("user_created", {
        "user_id": user_id,
        "name": name,
        "email": email
    })

    return {"message": "User created", "id": user_id}
