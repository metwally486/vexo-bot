from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional, List
import asyncio
import config
import database as db
from bot import register_handlers
from aiogram import Bot, Dispatcher

# ==================== إدارة دورة الحياة ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """إعدادات بدء وإيقاف التطبيق"""
    # Startup
    print("🚀 Starting Vexo Bot API...")
    
    # Initialize database
    db_success = await db.init_db()
    if not db_success:
        print("❌ Database connection failed!")
        raise Exception("Database connection failed")
    
    print("✅ Database connected successfully")
    
    # Initialize bot
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    register_handlers(dp)
    
    # Start bot polling in background
    asyncio.create_task(dp.start_polling(bot))
    print("✅ Bot started successfully")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    await db.close_db()
    await bot.close()  # تصحيح: استخدام close() بدلاً من session.close()
    print("✅ Shutdown complete")

# ==================== إعداد التطبيق ====================

app = FastAPI(
    title="Vexo Bot API",
    description="Telegram Bot API for Vexo Services",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== الأمان ====================

async def verify_token(x_api_key: str = Header(None)):
    """التحقق من مفتاح API"""
    if not hasattr(config, 'API_SECRET_KEY') or x_api_key != config.API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return True

# ==================== النقاط الأساسية ====================

@app.get("/")
async def root():
    """الصفحة الرئيسية"""
    return {
        "message": "Vexo Bot API is running! ✅",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health():
    """فحص صحة النظام"""
    db_health = await db.health_check()
    pool_stats = db.get_pool_info()
    
    return {
        "status": "healthy" if db_health else "unhealthy",
        "database": "connected" if db_health else "disconnected",
        "pool_stats": pool_stats
    }

# ==================== الطلبات (Orders) ====================

@app.get("/api/orders")
async def get_orders(api_key: str = Depends(verify_token)):
    """جلب جميع الطلبات"""
    orders = await db.get_all_orders()
    return orders

@app.get("/api/orders/{order_id}")
async def get_order(order_id: int, api_key: str = Depends(verify_token)):
    """جلب طلب محدد"""
    order = await db.get_order_by_id(order_id)
    if order:
        return order
    raise HTTPException(status_code=404, detail="Order not found")

@app.post("/api/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: str,
    api_key: str = Depends(verify_token)
):
    """تحديث حالة الطلب"""
    success = await db.update_order_status(order_id, status)
    if success:
        return {"message": "Status updated", "order_id": order_id, "status": status}
    raise HTTPException(status_code=500, detail="Failed to update status")

@app.post("/api/orders/{order_id}/notes")
async def update_order_notes(
    order_id: int,
    notes: str,
    api_key: str = Depends(verify_token)
):
    """إضافة ملاحظات للطلب"""
    success = await db.update_order_notes(order_id, notes)
    if success:
        return {"message": "Notes updated", "order_id": order_id}
    raise HTTPException(status_code=500, detail="Failed to update notes")

# ==================== المستخدمين (Users) ====================

@app.get("/api/users")
async def get_all_users(api_key: str = Depends(verify_token)):
    """جلب جميع المستخدمين"""
    users = await db.get_all_users()
    return users

@app.get("/api/users/{user_id}")
async def get_user(user_id: int, api_key: str = Depends(verify_token)):
    """جلب مستخدم محدد"""
    user = await db.get_user(user_id)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/api/users/{user_id}/points")
async def update_user_points(
    user_id: int,
    points: int,
    api_key: str = Depends(verify_token)
):
    """تحديث نقاط المستخدم (تعيين القيمة المطلقة)"""
    user = await db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    current_points = user.get('loyalty_points', 0)
    diff = points - current_points
    
    if diff > 0:
        await db.add_points(user_id, diff)
    elif diff < 0:
        await db.deduct_points(user_id, abs(diff))
    
    return {
        "message": "Points updated",
        "user_id": user_id,
        "new_points": points
    }

# ==================== التذاكر (Tickets) ====================

@app.get("/api/tickets")
async def get_all_tickets(api_key: str = Depends(verify_token)):
    """جلب جميع التذاكر المفتوحة (يمكن تعديلها لجلب الكل)"""
    tickets = await db.get_all_open_tickets()
    return tickets

@app.get("/api/tickets/{ticket_id}")
async def get_ticket(ticket_id: int, api_key: str = Depends(verify_token)):
    """جلب تذكرة محددة"""
    # تحتاج إضافة دالة get_ticket في database.py إذا أردت استخدامها
    raise HTTPException(status_code=404, detail="Not implemented")

@app.post("/api/tickets/{ticket_id}/status")
async def update_ticket_status(
    ticket_id: int,
    status: str,
    api_key: str = Depends(verify_token)
):
    """تحديث حالة التذكرة (open/closed)"""
    success = await db.update_ticket_status(ticket_id, status)
    if success:
        return {"message": "Ticket status updated", "ticket_id": ticket_id}
    raise HTTPException(status_code=404, detail="Ticket not found")

@app.post("/api/tickets/{ticket_id}/reply")
async def add_ticket_reply(
    ticket_id: int,
    message: str,
    is_admin: bool = True,
    api_key: str = Depends(verify_token)
):
    """إضافة رد على تذكرة"""
    success = await db.add_ticket_reply(ticket_id, message, is_admin)
    if success:
        return {"message": "Reply added", "ticket_id": ticket_id}
    raise HTTPException(status_code=500, detail="Failed to add reply")

# ==================== معرض الأعمال (Portfolio) ====================

@app.get("/api/portfolio")
async def get_portfolio_items(
    project_type: Optional[str] = None,
    api_key: str = Depends(verify_token)
):
    """جلب مشاريع المعرض (جميعها أو حسب النوع)"""
    items = await db.get_portfolio(project_type)
    return items

@app.get("/api/portfolio/{item_id}")
async def get_portfolio_item(item_id: int, api_key: str = Depends(verify_token)):
    """جلب مشروع محدد"""
    item = await db.get_portfolio_item(item_id)
    if item:
        return item
    raise HTTPException(status_code=404, detail="Item not found")

@app.post("/api/portfolio")
async def create_portfolio_item(
    title: str,
    type: str,
    description: str = "",
    preview_link: str = "",
    image_url: str = "",
    price: str = "",
    features: str = "",
    api_key: str = Depends(verify_token)
):
    """إضافة مشروع جديد إلى معرض الأعمال"""
    item_id = await db.add_portfolio_item(
        title=title,
        project_type=type,
        description=description,
        preview_link=preview_link,
        image_url=image_url,
        price=price,
        features=features
    )
    if item_id:
        return {"message": "Portfolio item added", "id": item_id}
    raise HTTPException(status_code=500, detail="Failed to add portfolio item")

@app.put("/api/portfolio/{item_id}")
async def update_portfolio_item(
    item_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    preview_link: Optional[str] = None,
    image_url: Optional[str] = None,
    price: Optional[str] = None,
    features: Optional[str] = None,
    api_key: str = Depends(verify_token)
):
    """تحديث مشروع موجود"""
    success = await db.update_portfolio_item(
        item_id, title, description, preview_link, image_url, price, features
    )
    if success:
        return {"message": "Portfolio item updated", "id": item_id}
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/api/portfolio/{item_id}")
async def delete_portfolio_item(item_id: int, api_key: str = Depends(verify_token)):
    """حذف مشروع من المعرض"""
    success = await db.delete_portfolio_item(item_id)
    if success:
        return {"message": "Portfolio item deleted"}
    raise HTTPException(status_code=404, detail="Item not found")

# ==================== الخدمات (Services) ====================

@app.get("/api/services")
async def get_services(api_key: str = Depends(verify_token)):
    """جلب الخدمات المتاحة"""
    services = await db.get_services()
    return services

@app.post("/api/services")
async def create_service(
    name: str,
    price_range: str,
    icon: str = "🤖",
    api_key: str = Depends(verify_token)
):
    """إضافة خدمة جديدة"""
    service_id = await db.add_service(name, price_range, icon)
    if service_id:
        return {"message": "Service added", "id": service_id}
    raise HTTPException(status_code=500, detail="Failed to add service")

@app.delete("/api/services/{service_id}")
async def delete_service(service_id: int, api_key: str = Depends(verify_token)):
    """حذف خدمة"""
    success = await db.delete_service(service_id)
    if success:
        return {"message": "Service deleted"}
    raise HTTPException(status_code=404, detail="Service not found")

# ==================== الإحصائيات (Stats) ====================

@app.get("/api/stats")
async def get_stats(api_key: str = Depends(verify_token)):
    """جلب إحصائيات لوحة التحكم الرئيسية"""
    stats = await db.get_dashboard_stats()
    return stats

@app.get("/api/stats/weekly")
async def get_weekly_stats(api_key: str = Depends(verify_token)):
    """جلب إحصائيات الطلبات الأسبوعية"""
    weekly = await db.get_weekly_orders()
    return weekly

@app.get("/api/stats/monthly")
async def get_monthly_stats(api_key: str = Depends(verify_token)):
    """جلب إحصائيات الشهر الحالي"""
    monthly = await db.get_monthly_stats()
    return monthly

# ==================== تشغيل التطبيق ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
