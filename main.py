from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional
import asyncio
import config
import database as db
from bot import register_handlers
from aiogram import Bot, Dispatcher

@asynccontextmanager
async def lifespan(app: FastAPI):
    # بدء التشغيل
    await db.init_db()
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    register_handlers(dp)
    
    # تشغيل البوت في الخلفية
    asyncio.create_task(dp.start_polling(bot))
    
    yield
    
    # إيقاف التشغيل
    await bot.close()

app = FastAPI(lifespan=lifespan)

# السماح لجميع الروابط (لـ Render / Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# التحقق من المفتاح
async def verify_token(x_api_key: str = Header(None)):
    if not hasattr(config, 'API_SECRET_KEY') or x_api_key != config.API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return True

# ==================== نقاط API الأساسية ====================
@app.get("/")
async def root():
    return {"message": "Vexo Bot API is running! ✅"}

@app.get("/api/orders")
async def get_orders(api_key: str = Depends(verify_token)):
    orders = await db.get_all_orders()
    return orders

@app.post("/api/orders/{order_id}/status")
async def update_order_status(order_id: int, status: str, api_key: str = Depends(verify_token)):
    await db.update_order_status(order_id, status)
    return {"message": "Status updated successfully"}

# ==================== Portfolio API ====================
@app.get("/api/portfolio")
async def get_portfolio_items(
    project_type: Optional[str] = None,
    api_key: str = Depends(verify_token)
):
    """جلب مشاريع المعرض (جميعها أو حسب النوع)"""
    items = await db.get_portfolio(project_type)
    return items

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

@app.delete("/api/portfolio/{item_id}")
async def delete_portfolio_item(item_id: int, api_key: str = Depends(verify_token)):
    """حذف مشروع من المعرض"""
    success = await db.delete_portfolio_item(item_id)
    if success:
        return {"message": "Portfolio item deleted"}
    raise HTTPException(status_code=404, detail="Item not found")

# ==================== Users API ====================
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
    
    return {"message": "Points updated", "user_id": user_id, "new_points": points}

# ==================== Tickets API ====================
@app.get("/api/tickets")
async def get_all_tickets(api_key: str = Depends(verify_token)):
    """جلب جميع التذاكر المفتوحة (يمكن تعديلها لجلب الكل)"""
    # للحصول على الكل، يمكن تعديل الدالة أو إضافة معلمة
    tickets = await db.get_all_open_tickets()
    return tickets

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

# ==================== Stats API ====================
@app.get("/api/stats")
async def get_stats(api_key: str = Depends(verify_token)):
    """جلب إحصائيات لوحة التحكم"""
    stats = await db.get_dashboard_stats()
    return stats

# ==================== تشغيل الخادم ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
