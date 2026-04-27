"""
database.py — إدارة قاعدة بيانات Vexo Bot (Supabase / PostgreSQL)
يحتوي على: تهيئة الجداول، CRUD كامل للمستخدمين / الطلبات / التذاكر / المعرض / الخدمات
"""
import asyncpg
import config
from typing import Optional, Any
from datetime import datetime

# ─── Connection Pool ───────────────────────────────────────────
pool: Optional[asyncpg.Pool] = None


async def init_db() -> bool:
    """تهيئة pool الاتصال وإنشاء الجداول"""
    global pool
    if pool is not None:
        return True
    try:
        pool = await asyncpg.create_pool(
            config.DATABASE_URL,
            min_size=2,
            max_size=10,
            command_timeout=60,
            max_inactive_connection_lifetime=300.0,
            statement_cache_size=20,
        )
        print("✅ Database pool created")
        await _create_tables()
        return True
    except Exception as e:
        print(f"❌ Database init error: {e}")
        return False


async def close_db() -> None:
    """إغلاق pool بشكل آمن"""
    global pool
    if pool:
        await pool.close()
        pool = None
        print("✅ Database pool closed")


async def health_check() -> bool:
    try:
        if pool is None:
            return False
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return True
    except Exception:
        return False


def get_pool_info() -> dict:
    if pool:
        return {
            "size": pool.get_size(),
            "free": pool.get_free_size(),
            "min": pool._min_size,
            "max": pool._max_size,
        }
    return {"error": "pool not initialized"}


# ─── إنشاء الجداول ────────────────────────────────────────────
async def _create_tables() -> None:
    async with pool.acquire() as conn:
        # المستخدمون
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            BIGINT PRIMARY KEY,
                username      TEXT,
                full_name     TEXT,
                loyalty_points INTEGER DEFAULT 0,
                joined_channel_points BOOLEAN DEFAULT FALSE,
                is_blocked    BOOLEAN DEFAULT FALSE,
                joined_at     TIMESTAMPTZ DEFAULT NOW(),
                updated_at    TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        # الطلبات
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id           SERIAL PRIMARY KEY,
                user_id      BIGINT REFERENCES users(id) ON DELETE CASCADE,
                service_type TEXT NOT NULL,
                details      TEXT,
                budget       TEXT,
                status       TEXT DEFAULT 'pending'
                             CHECK (status IN ('pending','processing','completed','rejected','cancelled')),
                admin_notes  TEXT,
                created_at   TIMESTAMPTZ DEFAULT NOW(),
                updated_at   TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        # التذاكر
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id         SERIAL PRIMARY KEY,
                user_id    BIGINT REFERENCES users(id) ON DELETE CASCADE,
                subject    TEXT DEFAULT 'دعم عام',
                message    TEXT NOT NULL,
                status     TEXT DEFAULT 'open'
                           CHECK (status IN ('open','in_progress','closed')),
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        # ردود التذاكر
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS ticket_replies (
                id         SERIAL PRIMARY KEY,
                ticket_id  INTEGER REFERENCES tickets(id) ON DELETE CASCADE,
                sender_id  BIGINT,
                message    TEXT NOT NULL,
                is_admin   BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        # معرض الأعمال
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                id           SERIAL PRIMARY KEY,
                title        TEXT NOT NULL,
                type         TEXT NOT NULL,
                description  TEXT,
                image_url    TEXT,
                preview_link TEXT,
                price        TEXT,
                features     TEXT,
                is_active    BOOLEAN DEFAULT TRUE,
                created_at   TIMESTAMPTZ DEFAULT NOW(),
                updated_at   TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        # الخدمات
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id          SERIAL PRIMARY KEY,
                name        TEXT NOT NULL,
                price_range TEXT,
                icon        TEXT DEFAULT '🤖',
                description TEXT,
                is_active   BOOLEAN DEFAULT TRUE,
                created_at  TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        # سجل النقاط
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS points_log (
                id         SERIAL PRIMARY KEY,
                user_id    BIGINT REFERENCES users(id) ON DELETE CASCADE,
                amount     INTEGER NOT NULL,
                reason     TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)

        # بث للمستخدمين
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS broadcasts (
                id         SERIAL PRIMARY KEY,
                message    TEXT NOT NULL,
                sent_count INTEGER DEFAULT 0,
                admin_id   BIGINT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        """)

    print("✅ All tables verified / created")


# ══════════════════════════════════════════════════════════════
# المستخدمون
# ══════════════════════════════════════════════════════════════

async def upsert_user(user_id: int, username: Optional[str], full_name: Optional[str]) -> bool:
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO users (id, username, full_name)
                VALUES ($1, $2, $3)
                ON CONFLICT (id) DO UPDATE
                  SET username   = COALESCE(EXCLUDED.username,  users.username),
                      full_name  = COALESCE(EXCLUDED.full_name, users.full_name),
                      updated_at = NOW()
                """,
                user_id, username, full_name,
            )
        return True
    except Exception as e:
        print(f"❌ upsert_user: {e}")
        return False


async def get_user(user_id: int) -> Optional[dict]:
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
            return dict(row) if row else None
    except Exception as e:
        print(f"❌ get_user: {e}")
        return None


async def get_all_users(limit: int = 200) -> list[dict]:
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM users ORDER BY joined_at DESC LIMIT $1", limit
            )
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ get_all_users: {e}")
        return []


async def get_all_user_ids() -> list[int]:
    """لاستخدامه في البث"""
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id FROM users WHERE is_blocked = FALSE"
            )
            return [r["id"] for r in rows]
    except Exception as e:
        print(f"❌ get_all_user_ids: {e}")
        return []


async def block_user(user_id: int, blocked: bool = True) -> bool:
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET is_blocked = $1, updated_at = NOW() WHERE id = $2",
                blocked, user_id,
            )
        return True
    except Exception as e:
        print(f"❌ block_user: {e}")
        return False


async def add_points(user_id: int, amount: int, reason: str = "") -> bool:
    try:
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "UPDATE users SET loyalty_points = loyalty_points + $1, updated_at = NOW() WHERE id = $2",
                    amount, user_id,
                )
                await conn.execute(
                    "INSERT INTO points_log (user_id, amount, reason) VALUES ($1, $2, $3)",
                    user_id, amount, reason,
                )
        return True
    except Exception as e:
        print(f"❌ add_points: {e}")
        return False


async def deduct_points(user_id: int, amount: int, reason: str = "") -> bool:
    try:
        async with pool.acquire() as conn:
            async with conn.transaction():
                result = await conn.execute(
                    """
                    UPDATE users
                    SET loyalty_points = GREATEST(loyalty_points - $1, 0),
                        updated_at = NOW()
                    WHERE id = $2 AND loyalty_points >= $1
                    """,
                    amount, user_id,
                )
                if result == "UPDATE 0":
                    return False
                await conn.execute(
                    "INSERT INTO points_log (user_id, amount, reason) VALUES ($1, $2, $3)",
                    user_id, -amount, reason,
                )
        return True
    except Exception as e:
        print(f"❌ deduct_points: {e}")
        return False


async def set_points_absolute(user_id: int, new_points: int) -> bool:
    """تعيين نقاط بشكل مطلق (للـ API)"""
    try:
        user = await get_user(user_id)
        if not user:
            return False
        diff = new_points - user.get("loyalty_points", 0)
        if diff > 0:
            return await add_points(user_id, diff, "admin_set")
        elif diff < 0:
            return await deduct_points(user_id, abs(diff), "admin_set")
        return True
    except Exception as e:
        print(f"❌ set_points_absolute: {e}")
        return False


async def mark_channel_joined(user_id: int) -> bool:
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET joined_channel_points = TRUE, updated_at = NOW() WHERE id = $1",
                user_id,
            )
        return True
    except Exception as e:
        print(f"❌ mark_channel_joined: {e}")
        return False


async def get_user_channel_status(user_id: int) -> bool:
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT joined_channel_points FROM users WHERE id = $1", user_id
            )
            return bool(row["joined_channel_points"]) if row else False
    except Exception as e:
        print(f"❌ get_user_channel_status: {e}")
        return False


# ══════════════════════════════════════════════════════════════
# الطلبات
# ══════════════════════════════════════════════════════════════

async def create_order(
    user_id: int, service_type: str, details: str, budget: str
) -> Optional[int]:
    try:
        async with pool.acquire() as conn:
            order_id = await conn.fetchval(
                """
                INSERT INTO orders (user_id, service_type, details, budget)
                VALUES ($1, $2, $3, $4) RETURNING id
                """,
                user_id, service_type, details, budget,
            )
        return order_id
    except Exception as e:
        print(f"❌ create_order: {e}")
        return None


async def get_user_orders(user_id: int, limit: int = 20) -> list[dict]:
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM orders WHERE user_id = $1 ORDER BY created_at DESC LIMIT $2",
                user_id, limit,
            )
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ get_user_orders: {e}")
        return []


async def count_user_orders_today(user_id: int) -> int:
    try:
        async with pool.acquire() as conn:
            return await conn.fetchval(
                """
                SELECT COUNT(*) FROM orders
                WHERE user_id = $1
                  AND created_at >= NOW() - INTERVAL '1 day'
                """,
                user_id,
            )
    except Exception as e:
        print(f"❌ count_user_orders_today: {e}")
        return 0


async def get_all_orders(limit: int = 100) -> list[dict]:
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT o.*, u.username, u.full_name
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.id
                ORDER BY o.created_at DESC LIMIT $1
                """,
                limit,
            )
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ get_all_orders: {e}")
        return []


async def get_order_by_id(order_id: int) -> Optional[dict]:
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT o.*, u.username, u.full_name
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.id
                WHERE o.id = $1
                """,
                order_id,
            )
            return dict(row) if row else None
    except Exception as e:
        print(f"❌ get_order_by_id: {e}")
        return None


async def get_orders_by_status(status: str, limit: int = 50) -> list[dict]:
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM orders WHERE status=$1 ORDER BY created_at DESC LIMIT $2",
                status, limit,
            )
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ get_orders_by_status: {e}")
        return []


async def update_order_status(order_id: int, status: str) -> bool:
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE orders SET status=$1, updated_at=NOW() WHERE id=$2",
                status, order_id,
            )
        return True
    except Exception as e:
        print(f"❌ update_order_status: {e}")
        return False


async def update_order_notes(order_id: int, notes: str) -> bool:
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE orders
                SET admin_notes = COALESCE(admin_notes,'') || $1 || E'\n',
                    updated_at  = NOW()
                WHERE id = $2
                """,
                notes, order_id,
            )
        return True
    except Exception as e:
        print(f"❌ update_order_notes: {e}")
        return False


# ══════════════════════════════════════════════════════════════
# التذاكر
# ══════════════════════════════════════════════════════════════

async def create_ticket(user_id: int, subject: str, message: str) -> Optional[int]:
    try:
        async with pool.acquire() as conn:
            ticket_id = await conn.fetchval(
                "INSERT INTO tickets (user_id, subject, message) VALUES ($1,$2,$3) RETURNING id",
                user_id, subject, message,
            )
        return ticket_id
    except Exception as e:
        print(f"❌ create_ticket: {e}")
        return None


async def get_user_tickets(user_id: int, limit: int = 10) -> list[dict]:
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM tickets WHERE user_id=$1 ORDER BY created_at DESC LIMIT $2",
                user_id, limit,
            )
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ get_user_tickets: {e}")
        return []


async def count_user_open_tickets(user_id: int) -> int:
    try:
        async with pool.acquire() as conn:
            return await conn.fetchval(
                "SELECT COUNT(*) FROM tickets WHERE user_id=$1 AND status != 'closed'",
                user_id,
            )
    except Exception as e:
        print(f"❌ count_user_open_tickets: {e}")
        return 0


async def get_all_open_tickets(limit: int = 50) -> list[dict]:
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT t.*, u.username, u.full_name
                FROM tickets t
                LEFT JOIN users u ON t.user_id = u.id
                WHERE t.status != 'closed'
                ORDER BY t.created_at DESC LIMIT $1
                """,
                limit,
            )
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ get_all_open_tickets: {e}")
        return []


async def get_ticket_by_id(ticket_id: int) -> Optional[dict]:
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT t.*, u.username, u.full_name
                FROM tickets t
                LEFT JOIN users u ON t.user_id = u.id
                WHERE t.id = $1
                """,
                ticket_id,
            )
            return dict(row) if row else None
    except Exception as e:
        print(f"❌ get_ticket_by_id: {e}")
        return None


async def update_ticket_status(ticket_id: int, status: str) -> bool:
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE tickets SET status=$1, updated_at=NOW() WHERE id=$2",
                status, ticket_id,
            )
        return True
    except Exception as e:
        print(f"❌ update_ticket_status: {e}")
        return False


async def add_ticket_reply(
    ticket_id: int, sender_id: int, message: str, is_admin: bool = False
) -> bool:
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO ticket_replies (ticket_id, sender_id, message, is_admin)
                VALUES ($1, $2, $3, $4)
                """,
                ticket_id, sender_id, message, is_admin,
            )
        return True
    except Exception as e:
        print(f"❌ add_ticket_reply: {e}")
        return False


async def get_ticket_replies(ticket_id: int) -> list[dict]:
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT tr.*,
                       CASE WHEN tr.is_admin THEN 'الدعم' ELSE u.username END AS display_name
                FROM ticket_replies tr
                LEFT JOIN users u ON tr.sender_id = u.id
                WHERE tr.ticket_id = $1
                ORDER BY tr.created_at ASC
                """,
                ticket_id,
            )
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ get_ticket_replies: {e}")
        return []


# ══════════════════════════════════════════════════════════════
# معرض الأعمال
# ══════════════════════════════════════════════════════════════

async def add_portfolio_item(
    title: str,
    project_type: str,
    description: str = "",
    image_url: str = "",
    preview_link: str = "",
    price: str = "",
    features: str = "",
) -> Optional[int]:
    try:
        async with pool.acquire() as conn:
            item_id = await conn.fetchval(
                """
                INSERT INTO portfolio
                  (title, type, description, image_url, preview_link, price, features)
                VALUES ($1,$2,$3,$4,$5,$6,$7) RETURNING id
                """,
                title, project_type, description, image_url, preview_link, price, features,
            )
        return item_id
    except Exception as e:
        print(f"❌ add_portfolio_item: {e}")
        return None


async def get_portfolio(project_type: Optional[str] = None, limit: int = 20) -> list[dict]:
    try:
        async with pool.acquire() as conn:
            if project_type:
                rows = await conn.fetch(
                    "SELECT * FROM portfolio WHERE type=$1 AND is_active=TRUE ORDER BY created_at DESC LIMIT $2",
                    project_type, limit,
                )
            else:
                rows = await conn.fetch(
                    "SELECT * FROM portfolio WHERE is_active=TRUE ORDER BY created_at DESC LIMIT $1",
                    limit,
                )
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ get_portfolio: {e}")
        return []


async def get_portfolio_item(item_id: int) -> Optional[dict]:
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM portfolio WHERE id=$1", item_id)
            return dict(row) if row else None
    except Exception as e:
        print(f"❌ get_portfolio_item: {e}")
        return None


async def update_portfolio_item(item_id: int, **fields) -> bool:
    if not fields:
        return True
    try:
        allowed = {"title", "description", "image_url", "preview_link", "price", "features", "is_active"}
        cols, vals = [], []
        i = 1
        for k, v in fields.items():
            if k in allowed and v is not None:
                cols.append(f"{k}=${i}")
                vals.append(v)
                i += 1
        if not cols:
            return True
        cols.append("updated_at=NOW()")
        vals.append(item_id)
        async with pool.acquire() as conn:
            await conn.execute(
                f"UPDATE portfolio SET {', '.join(cols)} WHERE id=${i}", *vals
            )
        return True
    except Exception as e:
        print(f"❌ update_portfolio_item: {e}")
        return False


async def delete_portfolio_item(item_id: int) -> bool:
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE portfolio SET is_active=FALSE, updated_at=NOW() WHERE id=$1", item_id
            )
        return True
    except Exception as e:
        print(f"❌ delete_portfolio_item: {e}")
        return False


async def get_portfolio_count() -> int:
    try:
        async with pool.acquire() as conn:
            return await conn.fetchval("SELECT COUNT(*) FROM portfolio WHERE is_active=TRUE") or 0
    except Exception as e:
        print(f"❌ get_portfolio_count: {e}")
        return 0


# ══════════════════════════════════════════════════════════════
# الخدمات
# ══════════════════════════════════════════════════════════════

async def get_services() -> list[dict]:
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM services WHERE is_active=TRUE ORDER BY id"
            )
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ get_services: {e}")
        return []


async def add_service(
    name: str, price_range: str, icon: str = "🤖", description: str = ""
) -> Optional[int]:
    try:
        async with pool.acquire() as conn:
            sid = await conn.fetchval(
                "INSERT INTO services (name, price_range, icon, description) VALUES ($1,$2,$3,$4) RETURNING id",
                name, price_range, icon, description,
            )
        return sid
    except Exception as e:
        print(f"❌ add_service: {e}")
        return None


async def delete_service(service_id: int) -> bool:
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE services SET is_active=FALSE WHERE id=$1", service_id
            )
        return True
    except Exception as e:
        print(f"❌ delete_service: {e}")
        return False


# ══════════════════════════════════════════════════════════════
# الإحصائيات
# ══════════════════════════════════════════════════════════════

async def get_dashboard_stats() -> dict:
    try:
        async with pool.acquire() as conn:
            total_users   = await conn.fetchval("SELECT COUNT(*) FROM users") or 0
            total_orders  = await conn.fetchval("SELECT COUNT(*) FROM orders") or 0
            today_orders  = await conn.fetchval(
                "SELECT COUNT(*) FROM orders WHERE created_at >= NOW() - INTERVAL '1 day'"
            ) or 0
            open_tickets  = await conn.fetchval(
                "SELECT COUNT(*) FROM tickets WHERE status != 'closed'"
            ) or 0
            portfolio_cnt = await conn.fetchval(
                "SELECT COUNT(*) FROM portfolio WHERE is_active=TRUE"
            ) or 0
            total_points  = await conn.fetchval(
                "SELECT COALESCE(SUM(loyalty_points),0) FROM users"
            ) or 0
            status_rows   = await conn.fetch(
                "SELECT status, COUNT(*) AS cnt FROM orders GROUP BY status"
            )
            return {
                "total_users":     total_users,
                "total_orders":    total_orders,
                "today_orders":    today_orders,
                "open_tickets":    open_tickets,
                "portfolio_count": portfolio_cnt,
                "total_points":    total_points,
                "orders_by_status": {r["status"]: r["cnt"] for r in status_rows},
            }
    except Exception as e:
        print(f"❌ get_dashboard_stats: {e}")
        return {}


async def get_weekly_orders() -> list[dict]:
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT DATE_TRUNC('day', created_at) AS date, COUNT(*) AS count
                FROM orders
                WHERE created_at >= NOW() - INTERVAL '7 days'
                GROUP BY 1 ORDER BY 1
                """
            )
            return [{"date": str(r["date"])[:10], "count": r["count"]} for r in rows]
    except Exception as e:
        print(f"❌ get_weekly_orders: {e}")
        return []


async def get_monthly_stats() -> dict:
    try:
        async with pool.acquire() as conn:
            monthly_orders = await conn.fetchval(
                "SELECT COUNT(*) FROM orders WHERE created_at >= DATE_TRUNC('month', NOW())"
            ) or 0
            new_users = await conn.fetchval(
                "SELECT COUNT(*) FROM users WHERE joined_at >= DATE_TRUNC('month', NOW())"
            ) or 0
            revenue = await conn.fetchval(
                """
                SELECT COALESCE(SUM(
                    CASE
                        WHEN budget LIKE '%أقل من 100%' THEN 75
                        WHEN budget LIKE '%100%300%'    THEN 200
                        WHEN budget LIKE '%300%1000%'   THEN 650
                        WHEN budget LIKE '%أكثر من 1000%' THEN 1500
                        ELSE 0
                    END
                ), 0)
                FROM orders
                WHERE status='completed'
                  AND created_at >= DATE_TRUNC('month', NOW())
                """
            ) or 0
            return {
                "monthly_orders": monthly_orders,
                "new_users":      new_users,
                "estimated_revenue": revenue,
            }
    except Exception as e:
        print(f"❌ get_monthly_stats: {e}")
        return {}


# ══════════════════════════════════════════════════════════════
# البث
# ══════════════════════════════════════════════════════════════

async def log_broadcast(message: str, sent_count: int, admin_id: int) -> bool:
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO broadcasts (message, sent_count, admin_id) VALUES ($1,$2,$3)",
                message, sent_count, admin_id,
            )
        return True
    except Exception as e:
        print(f"❌ log_broadcast: {e}")
        return False


# ══════════════════════════════════════════════════════════════
# دوال مساعدة عامة
# ══════════════════════════════════════════════════════════════

def format_date(dt: Any) -> str:
    if dt is None:
        return "غير محدد"
    if hasattr(dt, "strftime"):
        return dt.strftime("%Y-%m-%d %H:%M")
    return str(dt)[:16]


def format_currency(amount: float, symbol: str = "$") -> str:
    return f"{symbol}{amount:,.2f}"


# ──────────────────────────────────────────────────────────────
__all__ = [
    "init_db", "close_db", "health_check", "get_pool_info",
    # users
    "upsert_user", "get_user", "get_all_users", "get_all_user_ids",
    "block_user", "add_points", "deduct_points", "set_points_absolute",
    "mark_channel_joined", "get_user_channel_status",
    # orders
    "create_order", "get_user_orders", "count_user_orders_today",
    "get_all_orders", "get_order_by_id", "get_orders_by_status",
    "update_order_status", "update_order_notes",
    # tickets
    "create_ticket", "get_user_tickets", "count_user_open_tickets",
    "get_all_open_tickets", "get_ticket_by_id",
    "update_ticket_status", "add_ticket_reply", "get_ticket_replies",
    # portfolio
    "add_portfolio_item", "get_portfolio", "get_portfolio_item",
    "update_portfolio_item", "delete_portfolio_item", "get_portfolio_count",
    # services
    "get_services", "add_service", "delete_service",
    # stats
    "get_dashboard_stats", "get_weekly_orders", "get_monthly_stats",
    # broadcast
    "log_broadcast",
    # helpers
    "format_date", "format_currency",
    ]
