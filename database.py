import asyncpg
import config
from typing import Optional, List, Dict, Any

# Global connection pool
pool = None

# ==================== إدارة الاتصال ====================

async def init_db():
    """تهيئة مجموعة اتصالات قاعدة البيانات مع إعدادات مثالية"""
    global pool
    
    if pool is None:
        try:
            pool = await asyncpg.create_pool(
                config.DATABASE_URL,
                min_size=2,              # الحد الأدنى للاتصالات
                max_size=10,             # الحد الأقصى (يمنع خطأ Max connections)
                command_timeout=60,      # مهلة التنفيذ: 60 ثانية
                max_inactive_connection_lifetime=300.0,  # إغلاق الاتصال الخامل بعد 5 دقائق
                statement_cache_size=10  # حجم ذاكرة التخزين المؤقت للاستعلامات
            )
            print("✅ Database connected successfully")
            print(f"📊 Pool: min=2, max=10, timeout=60s")
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            raise

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
    """الحصول على معلومات مجموعة الاتصالات"""    if pool:
        return {
            'size': pool.get_size(),
            'free_size': pool.get_free_size(),
            'min_size': pool._min_size,
            'max_size': pool._max_size
        }
    return {'error': 'Pool not initialized'}

# ==================== المستخدمين ====================

async def add_user(user_id: int, username: Optional[str], full_name: Optional[str]) -> bool:
    """إضافة مستخدم جديد أو تحديث بياناته"""
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
    """الحصول على بيانات مستخدم"""
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE id = $1",
                user_id
            )
            return dict(row) if row else None
    except Exception as e:
        print(f"❌ Error in get_user: {e}")
        return None

async def add_points(user_id: int, points: int) -> bool:
    """إضافة نقاط ولاء للمستخدم"""
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """                UPDATE users 
                SET loyalty_points = loyalty_points + $1,
                    updated_at = NOW()
                WHERE id = $2
                """,
                points, user_id
            )
            return True
    except Exception as e:
        print(f"❌ Error in add_points: {e}")
        return False

async def deduct_points(user_id: int, points: int) -> bool:
    """خصم نقاط من المستخدم (للاستبدال)"""
    try:
        async with pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE users 
                SET loyalty_points = GREATEST(loyalty_points - $1, 0),
                    updated_at = NOW()
                WHERE id = $2 AND loyalty_points >= $1
                """,
                points, user_id
            )
            return result == "UPDATE 1"
    except Exception as e:
        print(f"❌ Error in deduct_points: {e}")
        return False

# ==================== الطلبات ====================

async def create_order(
    user_id: int, 
    service_type: str, 
    details: str, 
    budget: str
) -> Optional[int]:
    """إنشاء طلب جديد"""
    try:
        async with pool.acquire() as conn:
            order_id = await conn.fetchval(
                """
                INSERT INTO orders (
                    user_id, service_type, details, budget, 
                    status, created_at
                ) 
                VALUES ($1, $2, $3, $4, 'pending', NOW()) 
                RETURNING id
                """,                user_id, service_type, details, budget
            )
            return order_id
    except Exception as e:
        print(f"❌ Error in create_order: {e}")
        return None

async def get_user_orders(user_id: int) -> List[Dict[str, Any]]:
    """الحصول على جميع طلبات مستخدم معين"""
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM orders 
                WHERE user_id = $1 
                ORDER BY created_at DESC
                LIMIT 20
                """,
                user_id
            )
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ Error in get_user_orders: {e}")
        return []

async def get_all_orders(limit: int = 100) -> List[Dict[str, Any]]:
    """الحصول على جميع الطلبات (للوحدة الإدارية)"""
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT o.*, u.username, u.full_name 
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.id
                ORDER BY o.created_at DESC
                LIMIT $1
                """,
                limit
            )
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ Error in get_all_orders: {e}")
        return []

async def get_order_by_id(order_id: int) -> Optional[Dict[str, Any]]:
    """الحصول على طلب محدد حسب الرقم"""
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """                SELECT o.*, u.username, u.full_name 
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.id
                WHERE o.id = $1
                """,
                order_id
            )
            return dict(row) if row else None
    except Exception as e:
        print(f"❌ Error in get_order_by_id: {e}")
        return None

async def update_order_status(order_id: int, status: str) -> bool:
    """تحديث حالة الطلب"""
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE orders 
                SET status = $1, updated_at = NOW()
                WHERE id = $2
                """,
                status, order_id
            )
            return True
    except Exception as e:
        print(f"❌ Error in update_order_status: {e}")
        return False

async def update_order_notes(order_id: int, notes: str) -> bool:
    """إضافة ملاحظات إدارية للطلب"""
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE orders 
                SET admin_notes = COALESCE(admin_notes, '') || $1 || E'\n',
                    updated_at = NOW()
                WHERE id = $2
                """,
                notes, order_id
            )
            return True
    except Exception as e:
        print(f"❌ Error in update_order_notes: {e}")
        return False

async def get_orders_by_status(status: str, limit: int = 50) -> List[Dict[str, Any]]:
    """الحصول على الطلبات حسب الحالة"""
    try:        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM orders 
                WHERE status = $1 
                ORDER BY created_at DESC
                LIMIT $2
                """,
                status, limit
            )
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ Error in get_orders_by_status: {e}")
        return []

# ==================== التذاكر ====================

async def create_ticket(user_id: int, message: str) -> Optional[int]:
    """فتح تذكرة دعم جديدة"""
    try:
        async with pool.acquire() as conn:
            ticket_id = await conn.fetchval(
                """
                INSERT INTO tickets (user_id, message, status, created_at) 
                VALUES ($1, $2, 'open', NOW()) 
                RETURNING id
                """,
                user_id, message
            )
            return ticket_id
    except Exception as e:
        print(f"❌ Error in create_ticket: {e}")
        return None

async def get_user_tickets(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """الحصول على تذاكر مستخدم معين"""
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM tickets 
                WHERE user_id = $1 
                ORDER BY created_at DESC
                LIMIT $2
                """,
                user_id, limit
            )
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ Error in get_user_tickets: {e}")        return []

async def get_all_open_tickets(limit: int = 50) -> List[Dict[str, Any]]:
    """الحصول على جميع التذاكر المفتوحة"""
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT t.*, u.username, u.full_name 
                FROM tickets t
                LEFT JOIN users u ON t.user_id = u.id
                WHERE t.status = 'open'
                ORDER BY t.created_at DESC
                LIMIT $1
                """,
                limit
            )
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ Error in get_all_open_tickets: {e}")
        return []

async def update_ticket_status(ticket_id: int, status: str) -> bool:
    """تحديث حالة التذكرة"""
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE tickets 
                SET status = $1, updated_at = NOW()
                WHERE id = $2
                """,
                status, ticket_id
            )
            return True
    except Exception as e:
        print(f"❌ Error in update_ticket_status: {e}")
        return False

async def add_ticket_reply(ticket_id: int, reply: str, is_admin: bool = True) -> bool:
    """إضافة رد على تذكرة"""
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO ticket_replies (
                    ticket_id, message, is_admin, created_at
                ) VALUES ($1, $2, $3, NOW())
                """,
                ticket_id, reply, is_admin            )
            return True
    except Exception as e:
        print(f"❌ Error in add_ticket_reply: {e}")
        return False

# ==================== الأعمال (Portfolio) ====================

async def add_portfolio_item(
    title: str,
    project_type: str,
    image_url: Optional[str],
    preview_link: Optional[str],
    description: Optional[str]
) -> Optional[int]:
    """إضافة مشروع جديد لمعرض الأعمال"""
    try:
        async with pool.acquire() as conn:
            item_id = await conn.fetchval(
                """
                INSERT INTO portfolio (
                    title, type, image_url, preview_link, 
                    description, created_at
                ) VALUES ($1, $2, $3, $4, $5, NOW())
                RETURNING id
                """,
                title, project_type, image_url, preview_link, description
            )
            return item_id
    except Exception as e:
        print(f"❌ Error in add_portfolio_item: {e}")
        return None

async def get_portfolio(project_type: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """الحصول على مشاريع معرض الأعمال"""
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
                    """                    SELECT * FROM portfolio 
                    ORDER BY created_at DESC
                    LIMIT $1
                    """,
                    limit
                )
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ Error in get_portfolio: {e}")
        return []

async def delete_portfolio_item(item_id: int) -> bool:
    """حذف مشروع من المعرض"""
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM portfolio WHERE id = $1",
                item_id
            )
            return True
    except Exception as e:
        print(f"❌ Error in delete_portfolio_item: {e}")
        return False

# ==================== الإحصائيات ====================

async def get_dashboard_stats() -> Dict[str, Any]:
    """الحصول على إحصائيات لوحة التحكم"""
    try:
        async with pool.acquire() as conn:
            # إجمالي المستخدمين
            total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
            
            # إجمالي الطلبات
            total_orders = await conn.fetchval("SELECT COUNT(*) FROM orders")
            
            # الطلبات حسب الحالة
            status_counts = await conn.fetch(
                "SELECT status, COUNT(*) as count FROM orders GROUP BY status"
            )
            
            # طلبات اليوم
            today_orders = await conn.fetchval(
                """
                SELECT COUNT(*) FROM orders 
                WHERE created_at >= NOW() - INTERVAL '1 day'
                """
            )
            
            # إجمالي النقاط الموزعة            total_points = await conn.fetchval(
                "SELECT COALESCE(SUM(loyalty_points), 0) FROM users"
            )
            
            # التذاكر المفتوحة
            open_tickets = await conn.fetchval(
                "SELECT COUNT(*) FROM tickets WHERE status = 'open'"
            )
            
            return {
                'total_users': total_users or 0,
                'total_orders': total_orders or 0,
                'orders_by_status': {r['status']: r['count'] for r in status_counts},
                'today_orders': today_orders or 0,
                'total_points': total_points or 0,
                'open_tickets': open_tickets or 0
            }
    except Exception as e:
        print(f"❌ Error in get_dashboard_stats: {e}")
        return {}

async def get_weekly_orders() -> List[Dict[str, Any]]:
    """الحصول على عدد الطلبات خلال الأسبوع الأخير"""
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT 
                    DATE_TRUNC('day', created_at) as date,
                    COUNT(*) as count
                FROM orders
                WHERE created_at >= NOW() - INTERVAL '7 days'
                GROUP BY DATE_TRUNC('day', created_at)
                ORDER BY date
                """
            )
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ Error in get_weekly_orders: {e}")
        return []

# ==================== الخدمات ====================

async def get_services() -> List[Dict[str, Any]]:
    """الحصول على قائمة الخدمات"""
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM services ORDER BY id")
            return [dict(r) for r in rows]
    except Exception as e:        print(f"❌ Error in get_services: {e}")
        return []

# ==================== دوال مساعدة ====================

async def execute_query(query: str, *args) -> Any:
    """تنفيذ استعلام مخصص (للاستخدام المتقدم)"""
    try:
        async with pool.acquire() as conn:
            return await conn.fetch(query, *args)
    except Exception as e:
        print(f"❌ Error in execute_query: {e}")
        return None

def format_date(dt) -> str:
    """تنسيق التاريخ للعرض"""
    if dt is None:
        return "N/A"
    if hasattr(dt, 'strftime'):
        return dt.strftime('%Y-%m-%d %H:%M')
    return str(dt)[:16]

# ==================== التصدير ====================

__all__ = [
    # إدارة الاتصال
    'init_db', 'close_db', 'health_check', 'get_pool_info',
    
    # المستخدمين
    'add_user', 'get_user', 'add_points', 'deduct_points',
    
    # الطلبات
    'create_order', 'get_user_orders', 'get_all_orders',
    'get_order_by_id', 'update_order_status', 'update_order_notes',
    'get_orders_by_status',
    
    # التذاكر
    'create_ticket', 'get_user_tickets', 'get_all_open_tickets',
    'update_ticket_status', 'add_ticket_reply',
    
    # الأعمال
    'add_portfolio_item', 'get_portfolio', 'delete_portfolio_item',
    
    # الإحصائيات
    'get_dashboard_stats', 'get_weekly_orders',
    
    # الخدمات
    'get_services',
    
    # مساعدة    'execute_query', 'format_date'
]
