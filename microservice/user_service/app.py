import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
import redis.asyncio as aioredis
import uuid

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

@app.on_event("startup")
async def startup():
    global db_pool, redis

    db_host = os.getenv("DB_HOST", "localhost")
    redis_host = os.getenv("REDIS_HOST", "localhost")

    db_pool = await asyncpg.create_pool(
        user=os.getenv("DB_USER", "user"),
        password=os.getenv("DB_PASSWORD", "userpass"),
        database=os.getenv("DB_NAME", "user_db"),
        host=db_host
    )

    redis = await aioredis.from_url(f"redis://{redis_host}", decode_responses=True)

@app.post("/user")
async def create_user():
    user_id = str(uuid.uuid4())
    name = "John Doe"
    email = "john@example.com"

    # Simpan ke database
    async with db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO users (id, name, email) VALUES ($1, $2, $3)",
            user_id, name, email
        )

    # Publish event ke Redis stream
    await redis.xadd("user_created", {
        "user_id": user_id,
        "name": name,
        "email": email
    })

    return {"message": "User created", "id": user_id}
