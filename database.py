import asyncpg
import config
from typing import Optional, List, Dict, Any
from datetime import datetime

# ==================== إعدادات الاتصال ====================
pool = None

async def init_db():
    """تهيئة مجموعة اتصالات قاعدة البيانات مع إعدادات مثالية"""
    global pool
    
    if pool is None:
        try:
            pool = await asyncpg.create_pool(
                config.DATABASE_URL,
                min_size=2,
                max_size=10,
                command_timeout=60,
                max_inactive_connection_lifetime=300.0,
                statement_cache_size=10
            )
            print("✅ Database connected successfully")
            print(f"📊 Pool: min=2, max=10, timeout=60s")
            await create_tables()
            return True
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            return False
    return True

async def create_tables():
    """إنشاء الجداول إذا لم تكن موجودة (مع الأعمدة الجديدة)"""
    async with pool.acquire() as conn:
        # جدول المستخدمين (مع joined_channel_points)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                loyalty_points INTEGER DEFAULT 0,
                joined_channel_points BOOLEAN DEFAULT FALSE,
                joined_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        # جدول الطلبات
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(id),
                service_type TEXT,
                details TEXT,
                budget TEXT,
                status TEXT DEFAULT 'pending',
                admin_notes TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        # جدول التذاكر
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(id),
                message TEXT,
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        # جدول ردود التذاكر
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS ticket_replies (
                id SERIAL PRIMARY KEY,
                ticket_id INTEGER REFERENCES tickets(id),
                message TEXT,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        # جدول معرض الأعمال (مع الأعمدة الجديدة)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                id SERIAL PRIMARY KEY,
                title TEXT,
                type TEXT,
                description TEXT,
                image_url TEXT,
                preview_link TEXT,
                price TEXT,
                features TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        # جدول الخدمات
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id SERIAL PRIMARY KEY,
                name TEXT,
                price_range TEXT,
                icon TEXT
            )
        """)
        print("✅ Tables created/verified with all required columns")

async def close_db():
    """إغلاق مجموعة الاتصالات بشكل آمن"""
    global pool
    if pool is not None:
        await pool.close()
        pool = None
        print("✅ Database connections closed")

async def health_check() -> bool:
    """فحص صحة الاتصال بقاعدة البيانات"""
    try:
        if pool is None:
            return False
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return True
    except:
        return False

def get_pool_info() -> Dict[str, Any]:
    """الحصول على معلومات مجموعة الاتصالات"""
    if pool:
        return {
            'size': pool.get_size(),
            'free_size': pool.get_free_size(),
            'min_size': pool._min_size,
            'max_size': pool._max_size
        }
    return {'error': 'Pool not initialized'}

# ==================== إدارة المستخدمين ====================

async def add_user(user_id: int, username: Optional[str], full_name: Optional[str]) -> bool:
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO users (id, username, full_name, joined_at) 
                VALUES ($1, $2, $3, NOW()) 
                ON CONFLICT (id) DO UPDATE
                SET username = COALESCE(EXCLUDED.username, users.username),
                    full_name = COALESCE(EXCLUDED.full_name, users.full_name),
                    updated_at = NOW()
                """,
                user_id, username, full_name
            )
            return True
    except Exception as e:
        print(f"❌ Error in add_user: {e}")
        return False

async def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
            return dict(row) if row else None
    except Exception as e:
        print(f"❌ Error in get_user: {e}")
        return None

async def add_points(user_id: int, points: int) -> bool:
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET loyalty_points = loyalty_points + $1, updated_at = NOW() WHERE id = $2",
                points, user_id
            )
            return True
    except Exception as e:
        print(f"❌ Error in add_points: {e}")
        return False

async def deduct_points(user_id: int, points: int) -> bool:
    try:
        async with pool.acquire() as conn:
            result = await conn.execute(
                "UPDATE users SET loyalty_points = GREATEST(loyalty_points - $1, 0), updated_at = NOW() WHERE id = $2 AND loyalty_points >= $1",
                points, user_id
            )
            return result == "UPDATE 1"
    except Exception as e:
        print(f"❌ Error in deduct_points: {e}")
        return False

async def get_all_users(limit: int = 100) -> List[Dict[str, Any]]:
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM users ORDER BY joined_at DESC LIMIT $1", limit)
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ Error in get_all_users: {e}")
        return []

async def mark_channel_joined(user_id: int) -> bool:
    """تحديد أن المستخدم انضم للقناة وحصل على النقاط"""
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE users 
                SET joined_channel_points = TRUE,
                    updated_at = NOW()
                WHERE id = $1
                """,
                user_id
            )
            return True
    except Exception as e:
        print(f"❌ Error in mark_channel_joined: {e}")
        return False

async def get_user_channel_status(user_id: int) -> bool:
    """التحقق إذا كان المستخدم قد حصل على نقاط القناة"""
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT joined_channel_points FROM users WHERE id = $1",
                user_id
            )
            return row['joined_channel_points'] if row else False
    except Exception as e:
        print(f"❌ Error in get_user_channel_status: {e}")
        return False

# ==================== إدارة الطلبات ====================

async def create_order(user_id: int, service_type: str, details: str, budget: str) -> Optional[int]:
    try:
        async with pool.acquire() as conn:
            order_id = await conn.fetchval(
                """
                INSERT INTO orders (user_id, service_type, details, budget, status, created_at) 
                VALUES ($1, $2, $3, $4, 'pending', NOW()) 
                RETURNING id
                """,
                user_id, service_type, details, budget
            )
            return order_id
    except Exception as e:
        print(f"❌ Error in create_order: {e}")
        return None

async def get_user_orders(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM orders WHERE user_id = $1 ORDER BY created_at DESC LIMIT $2", user_id, limit)
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ Error in get_user_orders: {e}")
        return []

async def get_all_orders(limit: int = 100) -> List[Dict[str, Any]]:
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT o.*, u.username, u.full_name 
                FROM orders o LEFT JOIN users u ON o.user_id = u.id
                ORDER BY o.created_at DESC LIMIT $1
                """, limit
            )
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ Error in get_all_orders: {e}")
        return []

async def get_order_by_id(order_id: int) -> Optional[Dict[str, Any]]:
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT o.*, u.username, u.full_name FROM orders o LEFT JOIN users u ON o.user_id = u.id WHERE o.id = $1",
                order_id
            )
            return dict(row) if row else None
    except Exception as e:
        print(f"❌ Error in get_order_by_id: {e}")
        return None

async def update_order_status(order_id: int, status: str) -> bool:
    try:
        async with pool.acquire() as conn:
            await conn.execute("UPDATE orders SET status = $1, updated_at = NOW() WHERE id = $2", status, order_id)
            return True
    except Exception as e:
        print(f"❌ Error in update_order_status: {e}")
        return False

async def update_order_notes(order_id: int, notes: str) -> bool:
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE orders SET admin_notes = COALESCE(admin_notes, '') || $1 || E'\n', updated_at = NOW() WHERE id = $2",
                notes, order_id
            )
            return True
    except Exception as e:
        print(f"❌ Error in update_order_notes: {e}")
        return False

async def get_orders_by_status(status: str, limit: int = 50) -> List[Dict[str, Any]]:
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM orders WHERE status = $1 ORDER BY created_at DESC LIMIT $2", status, limit)
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ Error in get_orders_by_status: {e}")
        return []

# ==================== إدارة التذاكر ====================

async def create_ticket(user_id: int, message: str) -> Optional[int]:
    try:
        async with pool.acquire() as conn:
            ticket_id = await conn.fetchval(
                "INSERT INTO tickets (user_id, message, status, created_at) VALUES ($1, $2, 'open', NOW()) RETURNING id",
                user_id, message
            )
            return ticket_id
    except Exception as e:
        print(f"❌ Error in create_ticket: {e}")
        return None

async def get_user_tickets(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM tickets WHERE user_id = $1 ORDER BY created_at DESC LIMIT $2", user_id, limit)
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ Error in get_user_tickets: {e}")
        return []

async def get_all_open_tickets(limit: int = 50) -> List[Dict[str, Any]]:
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT t.*, u.username, u.full_name 
                FROM tickets t LEFT JOIN users u ON t.user_id = u.id
                WHERE t.status = 'open' ORDER BY t.created_at DESC LIMIT $1
                """, limit
            )
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ Error in get_all_open_tickets: {e}")
        return []

async def update_ticket_status(ticket_id: int, status: str) -> bool:
    try:
        async with pool.acquire() as conn:
            await conn.execute("UPDATE tickets SET status = $1, updated_at = NOW() WHERE id = $2", status, ticket_id)
            return True
    except Exception as e:
        print(f"❌ Error in update_ticket_status: {e}")
        return False

async def add_ticket_reply(ticket_id: int, message: str, is_admin: bool = True) -> bool:
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO ticket_replies (ticket_id, message, is_admin, created_at) VALUES ($1, $2, $3, NOW())",
                ticket_id, message, is_admin
            )
            return True
    except Exception as e:
        print(f"❌ Error in add_ticket_reply: {e}")
        return False

async def get_ticket_replies(ticket_id: int) -> List[Dict[str, Any]]:
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT tr.*, 
                       CASE WHEN tr.is_admin THEN 'admin' ELSE u.username END as username
                FROM ticket_replies tr
                LEFT JOIN users u ON tr.is_admin = FALSE AND u.id = tr.ticket_id
                WHERE tr.ticket_id = $1
                ORDER BY tr.created_at ASC
                """, ticket_id
            )
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ Error in get_ticket_replies: {e}")
        return []

# ==================== إدارة معرض الأعمال (Portfolio) ====================

async def add_portfolio_item(
    title: str,
    project_type: str,
    description: str = "",
    image_url: str = "",
    preview_link: str = "",
    price: str = "",
    features: str = ""
) -> Optional[int]:
    try:
        async with pool.acquire() as conn:
            item_id = await conn.fetchval(
                """
                INSERT INTO portfolio (
                    title, type, description, image_url, 
                    preview_link, price, features, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
                RETURNING id
                """,
                title, project_type, description, image_url, preview_link, price, features
            )
            return item_id
    except Exception as e:
        print(f"❌ Error in add_portfolio_item: {e}")
        return None

async def get_portfolio(project_type: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    try:
        async with pool.acquire() as conn:
            if project_type:
                rows = await conn.fetch(
                    """
                    SELECT * FROM portfolio 
                    WHERE type = $1 
                    ORDER BY created_at DESC
                    LIMIT $2
                    """,
                    project_type, limit
                )
            else:
                rows = await conn.fetch(
                    "SELECT * FROM portfolio ORDER BY created_at DESC LIMIT $1",
                    limit
                )
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ Error in get_portfolio: {e}")
        return []

async def get_portfolio_item(item_id: int) -> Optional[Dict[str, Any]]:
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM portfolio WHERE id = $1", item_id)
            return dict(row) if row else None
    except Exception as e:
        print(f"❌ Error in get_portfolio_item: {e}")
        return None

async def update_portfolio_item(
    item_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    image_url: Optional[str] = None,
    preview_link: Optional[str] = None,
    price: Optional[str] = None,
    features: Optional[str] = None
) -> bool:
    try:
        async with pool.acquire() as conn:
            updates = []
            values = []
            param_index = 1
            
            if title is not None:
                updates.append(f"title = ${param_index}")
                values.append(title)
                param_index += 1
            if description is not None:
                updates.append(f"description = ${param_index}")
                values.append(description)
                param_index += 1
            if image_url is not None:
                updates.append(f"image_url = ${param_index}")
                values.append(image_url)
                param_index += 1
            if preview_link is not None:
                updates.append(f"preview_link = ${param_index}")
                values.append(preview_link)
                param_index += 1
            if price is not None:
                updates.append(f"price = ${param_index}")
                values.append(price)
                param_index += 1
            if features is not None:
                updates.append(f"features = ${param_index}")
                values.append(features)
                param_index += 1
            
            if updates:
                updates.append("updated_at = NOW()")
                values.append(item_id)
                query = f"UPDATE portfolio SET {', '.join(updates)} WHERE id = ${param_index}"
                await conn.execute(query, *values)
            return True
    except Exception as e:
        print(f"❌ Error in update_portfolio_item: {e}")
        return False

async def delete_portfolio_item(item_id: int) -> bool:
    try:
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM portfolio WHERE id = $1", item_id)
            return True
    except Exception as e:
        print(f"❌ Error in delete_portfolio_item: {e}")
        return False

async def get_portfolio_count() -> int:
    try:
        async with pool.acquire() as conn:
            count = await conn.fetchval("SELECT COUNT(*) FROM portfolio")
            return count or 0
    except Exception as e:
        print(f"❌ Error in get_portfolio_count: {e}")
        return 0

# ==================== إدارة الخدمات ====================

async def get_services() -> List[Dict[str, Any]]:
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM services ORDER BY id")
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ Error in get_services: {e}")
        return []

async def add_service(name: str, price_range: str, icon: str = "🤖") -> Optional[int]:
    try:
        async with pool.acquire() as conn:
            service_id = await conn.fetchval(
                "INSERT INTO services (name, price_range, icon) VALUES ($1, $2, $3) RETURNING id",
                name, price_range, icon
            )
            return service_id
    except Exception as e:
        print(f"❌ Error in add_service: {e}")
        return None

async def delete_service(service_id: int) -> bool:
    try:
        async with pool.acquire() as conn:
            await conn.execute("DELETE FROM services WHERE id = $1", service_id)
            return True
    except Exception as e:
        print(f"❌ Error in delete_service: {e}")
        return False

# ==================== الإحصائيات ====================

async def get_dashboard_stats() -> Dict[str, Any]:
    try:
        async with pool.acquire() as conn:
            total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
            total_orders = await conn.fetchval("SELECT COUNT(*) FROM orders")
            status_counts = await conn.fetch("SELECT status, COUNT(*) as count FROM orders GROUP BY status")
            today_orders = await conn.fetchval("SELECT COUNT(*) FROM orders WHERE created_at >= NOW() - INTERVAL '1 day'")
            total_points = await conn.fetchval("SELECT COALESCE(SUM(loyalty_points), 0) FROM users")
            open_tickets = await conn.fetchval("SELECT COUNT(*) FROM tickets WHERE status = 'open'")
            portfolio_count = await conn.fetchval("SELECT COUNT(*) FROM portfolio")
            return {
                'total_users': total_users or 0,
                'total_orders': total_orders or 0,
                'orders_by_status': {r['status']: r['count'] for r in status_counts},
                'today_orders': today_orders or 0,
                'total_points': total_points or 0,
                'open_tickets': open_tickets or 0,
                'portfolio_count': portfolio_count or 0
            }
    except Exception as e:
        print(f"❌ Error in get_dashboard_stats: {e}")
        return {}

async def get_weekly_orders() -> List[Dict[str, Any]]:
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT DATE_TRUNC('day', created_at) as date, COUNT(*) as count
                FROM orders WHERE created_at >= NOW() - INTERVAL '7 days'
                GROUP BY DATE_TRUNC('day', created_at) ORDER BY date
                """
            )
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ Error in get_weekly_orders: {e}")
        return []

async def get_monthly_stats() -> Dict[str, Any]:
    try:
        async with pool.acquire() as conn:
            monthly_orders = await conn.fetchval(
                "SELECT COUNT(*) FROM orders WHERE created_at >= DATE_TRUNC('month', NOW())"
            )
            new_users = await conn.fetchval(
                "SELECT COUNT(*) FROM users WHERE joined_at >= DATE_TRUNC('month', NOW())"
            )
            estimated_revenue = await conn.fetchval(
                """
                SELECT COALESCE(SUM(
                    CASE 
                        WHEN budget LIKE '%أقل من 100%' THEN 75
                        WHEN budget LIKE '%100$ - 300%' THEN 200
                        WHEN budget LIKE '%300$ - 1000%' THEN 650
                        WHEN budget LIKE '%أكثر من 1000%' THEN 1500
                        ELSE 0
                    END
                ), 0) FROM orders 
                WHERE status = 'completed' AND created_at >= DATE_TRUNC('month', NOW())
                """
            )
            return {
                'monthly_orders': monthly_orders or 0,
                'new_users': new_users or 0,
                'estimated_revenue': estimated_revenue or 0
            }
    except Exception as e:
        print(f"❌ Error in get_monthly_stats: {e}")
        return {}

# ==================== دوال مساعدة ====================

async def execute_query(query: str, *args) -> Any:
    try:
        async with pool.acquire() as conn:
            return await conn.fetch(query, *args)
    except Exception as e:
        print(f"❌ Error in execute_query: {e}")
        return None

def format_date(dt) -> str:
    if dt is None:
        return "N/A"
    if hasattr(dt, 'strftime'):
        return dt.strftime('%Y-%m-%d %H:%M')
    return str(dt)[:16]

def format_currency(amount: float, currency: str = '$') -> str:
    return f"{currency}{amount:,.2f}"

# ==================== التصدير ====================

__all__ = [
    # إدارة الاتصال
    'init_db', 'close_db', 'health_check', 'get_pool_info',
    # المستخدمين
    'add_user', 'get_user', 'add_points', 'deduct_points', 'get_all_users',
    'mark_channel_joined', 'get_user_channel_status',
    # الطلبات
    'create_order', 'get_user_orders', 'get_all_orders',
    'get_order_by_id', 'update_order_status', 'update_order_notes',
    'get_orders_by_status',
    # التذاكر
    'create_ticket', 'get_user_tickets', 'get_all_open_tickets',
    'update_ticket_status', 'add_ticket_reply', 'get_ticket_replies',
    # معرض الأعمال
    'add_portfolio_item', 'get_portfolio', 'get_portfolio_item',
    'update_portfolio_item', 'delete_portfolio_item', 'get_portfolio_count',
    # الخدمات
    'get_services', 'add_service', 'delete_service',
    # الإحصائيات
    'get_dashboard_stats', 'get_weekly_orders', 'get_monthly_stats',
    # دوال مساعدة
    'execute_query', 'format_date', 'format_currency'
]
