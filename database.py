import asyncpg
import config

pool = None

async def init_db():
    global pool
    pool = await asyncpg.create_pool(config.DATABASE_URL)
    print("✅ Database connected")

async def add_user(user_id, username, full_name):
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO users (id, username, full_name) VALUES ($1, $2, $3) ON CONFLICT (id) DO NOTHING",
            user_id, username, full_name
        )

async def create_order(user_id, service_type, details, budget):
    async with pool.acquire() as conn:
        return await conn.fetchval(
            "INSERT INTO orders (user_id, service_type, details, budget) VALUES ($1, $2, $3, $4) RETURNING id",
            user_id, service_type, details, budget
        )

async def get_user_orders(user_id):
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM orders WHERE user_id = $1 ORDER BY created_at DESC", user_id)
        return [dict(r) for r in rows]

async def get_all_orders():
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM orders ORDER BY created_at DESC")
        return [dict(r) for r in rows]

async def update_order_status(order_id, status):
    async with pool.acquire() as conn:
        await conn.execute("UPDATE orders SET status = $1 WHERE id = $2", status, order_id)

async def get_user(user_id):
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
