"""
main.py — نقطة دخول Vexo Bot
يشغّل FastAPI + aiogram معاً في نفس العملية
"""
import asyncio
import threading
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from typing import Optional
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import config
import database as db
from bot import register_handlers

# ─── التحقق من الإعدادات عند البدء ───────────────────────────
missing = config.validate_config()
if missing:
    print(f"❌ متغيرات بيئة مفقودة: {', '.join(missing)}")
    sys.exit(1)


# ══════════════════════════════════════════════════════════════
# دورة حياة التطبيق
# ══════════════════════════════════════════════════════════════

bot_instance: Optional[Bot] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot_instance
    print("🚀 Starting Vexo Bot...")

    # قاعدة البيانات
    ok = await db.init_db()
    if not ok:
        print("❌ فشل الاتصال بقاعدة البيانات!")
        raise RuntimeError("Database connection failed")

    # البوت
    bot_instance = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    register_handlers(dp)
    asyncio.create_task(dp.start_polling(bot_instance, allowed_updates=["message", "callback_query"]))
    print("✅ Bot polling started")

    yield

    # إيقاف آمن
    print("🛑 Shutting down...")
    await bot_instance.close()
    await db.close_db()
    print("✅ Shutdown complete")


# ══════════════════════════════════════════════════════════════
# FastAPI App
# ══════════════════════════════════════════════════════════════

app = FastAPI(
    title="Vexo Bot API",
    description="🤖 Telegram Bot API for Vexo Services",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── مصادقة API ───────────────────────────────────────────────

async def verify_token(x_api_key: str = Header(None)) -> bool:
    if x_api_key != config.API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return True


# ══════════════════════════════════════════════════════════════
# المسارات الأساسية
# ══════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse, tags=["Health"])
async def root():
    return """
    <html><head><title>Vexo Bot</title></head>
    <body style="font-family:sans-serif; text-align:center; padding:50px;">
        <h1>🤖 Vexo Bot API</h1>
        <p>✅ يعمل بنجاح</p>
        <a href="/docs">📖 API Docs</a>
    </body></html>
    """


@app.get("/health", tags=["Health"])
async def health():
    ok = await db.health_check()
    return {
        "status": "healthy" if ok else "degraded",
        "database": "connected" if ok else "disconnected",
        "pool": db.get_pool_info(),
        "version": "2.0.0",
    }


# ══════════════════════════════════════════════════════════════
# الطلبات
# ══════════════════════════════════════════════════════════════

@app.get("/api/orders", tags=["Orders"])
async def get_orders(_: bool = Depends(verify_token)):
    return await db.get_all_orders()


@app.get("/api/orders/{order_id}", tags=["Orders"])
async def get_order(order_id: int, _: bool = Depends(verify_token)):
    order = await db.get_order_by_id(order_id)
    if not order:
        raise HTTPException(404, "Order not found")
    return order


@app.post("/api/orders/{order_id}/status", tags=["Orders"])
async def update_order_status(order_id: int, status: str, _: bool = Depends(verify_token)):
    valid = {"pending", "processing", "completed", "rejected", "cancelled"}
    if status not in valid:
        raise HTTPException(400, f"Invalid status. Must be one of: {valid}")
    ok = await db.update_order_status(order_id, status)
    if not ok:
        raise HTTPException(500, "Failed to update")

    # إشعار المستخدم عبر البوت
    order = await db.get_order_by_id(order_id)
    if order and bot_instance:
        STATUS_MSGS = {
            "completed":  "✅ تم إكمال طلبك!",
            "processing": "⚙️ بدأنا العمل على طلبك!",
            "rejected":   "❌ تم رفض طلبك.",
            "cancelled":  "🚫 تم إلغاء طلبك.",
        }
        msg = STATUS_MSGS.get(status)
        if msg:
            try:
                await bot_instance.send_message(
                    order["user_id"],
                    f"📦 <b>تحديث طلبك #{order_id}</b>\n\n{msg}",
                    parse_mode="HTML",
                )
            except Exception:
                pass

    return {"message": "Updated", "order_id": order_id, "status": status}


@app.post("/api/orders/{order_id}/notes", tags=["Orders"])
async def add_order_notes(order_id: int, notes: str, _: bool = Depends(verify_token)):
    ok = await db.update_order_notes(order_id, notes)
    if not ok:
        raise HTTPException(500, "Failed to update notes")
    return {"message": "Notes added", "order_id": order_id}


# ══════════════════════════════════════════════════════════════
# المستخدمون
# ══════════════════════════════════════════════════════════════

@app.get("/api/users", tags=["Users"])
async def get_users(_: bool = Depends(verify_token)):
    return await db.get_all_users()


@app.get("/api/users/{user_id}", tags=["Users"])
async def get_user(user_id: int, _: bool = Depends(verify_token)):
    user = await db.get_user(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user


@app.post("/api/users/{user_id}/points", tags=["Users"])
async def update_user_points(user_id: int, points: int, _: bool = Depends(verify_token)):
    ok = await db.set_points_absolute(user_id, points)
    if not ok:
        raise HTTPException(404, "User not found or operation failed")
    return {"message": "Points updated", "user_id": user_id, "new_points": points}


@app.post("/api/users/{user_id}/block", tags=["Users"])
async def toggle_block(user_id: int, blocked: bool = True, _: bool = Depends(verify_token)):
    await db.block_user(user_id, blocked)
    return {"message": f"User {'blocked' if blocked else 'unblocked'}", "user_id": user_id}


# ══════════════════════════════════════════════════════════════
# التذاكر
# ══════════════════════════════════════════════════════════════

@app.get("/api/tickets", tags=["Tickets"])
async def get_tickets(_: bool = Depends(verify_token)):
    return await db.get_all_open_tickets()


@app.get("/api/tickets/{ticket_id}", tags=["Tickets"])
async def get_ticket(ticket_id: int, _: bool = Depends(verify_token)):
    ticket = await db.get_ticket_by_id(ticket_id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    replies = await db.get_ticket_replies(ticket_id)
    return {"ticket": ticket, "replies": replies}


@app.post("/api/tickets/{ticket_id}/status", tags=["Tickets"])
async def update_ticket(ticket_id: int, status: str, _: bool = Depends(verify_token)):
    ok = await db.update_ticket_status(ticket_id, status)
    if not ok:
        raise HTTPException(500, "Failed to update")
    return {"message": "Updated", "ticket_id": ticket_id, "status": status}


@app.post("/api/tickets/{ticket_id}/reply", tags=["Tickets"])
async def reply_ticket(
    ticket_id: int, message: str, _: bool = Depends(verify_token)
):
    ok = await db.add_ticket_reply(ticket_id, config.ADMIN_ID, message, is_admin=True)
    if not ok:
        raise HTTPException(500, "Failed to add reply")

    ticket = await db.get_ticket_by_id(ticket_id)
    if ticket and bot_instance:
        try:
            await bot_instance.send_message(
                ticket["user_id"],
                f"💬 <b>رد على تذكرتك #{ticket_id}</b>\n\n{message}",
                parse_mode="HTML",
            )
        except Exception:
            pass

    return {"message": "Reply sent", "ticket_id": ticket_id}


# ══════════════════════════════════════════════════════════════
# معرض الأعمال
# ══════════════════════════════════════════════════════════════

@app.get("/api/portfolio", tags=["Portfolio"])
async def get_portfolio(project_type: Optional[str] = None, _: bool = Depends(verify_token)):
    return await db.get_portfolio(project_type)


@app.get("/api/portfolio/{item_id}", tags=["Portfolio"])
async def get_portfolio_item(item_id: int, _: bool = Depends(verify_token)):
    item = await db.get_portfolio_item(item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    return item


@app.post("/api/portfolio", tags=["Portfolio"])
async def create_portfolio_item(
    title: str,
    type: str,
    description: str = "",
    preview_link: str = "",
    image_url: str = "",
    price: str = "",
    features: str = "",
    _: bool = Depends(verify_token),
):
    item_id = await db.add_portfolio_item(
        title, type, description, image_url, preview_link, price, features
    )
    if not item_id:
        raise HTTPException(500, "Failed to add item")
    return {"message": "Created", "id": item_id}


@app.put("/api/portfolio/{item_id}", tags=["Portfolio"])
async def update_portfolio_item(
    item_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    preview_link: Optional[str] = None,
    image_url: Optional[str] = None,
    price: Optional[str] = None,
    features: Optional[str] = None,
    _: bool = Depends(verify_token),
):
    ok = await db.update_portfolio_item(
        item_id,
        title=title,
        description=description,
        preview_link=preview_link,
        image_url=image_url,
        price=price,
        features=features,
    )
    if not ok:
        raise HTTPException(404, "Item not found")
    return {"message": "Updated", "id": item_id}


@app.delete("/api/portfolio/{item_id}", tags=["Portfolio"])
async def delete_portfolio_item(item_id: int, _: bool = Depends(verify_token)):
    ok = await db.delete_portfolio_item(item_id)
    if not ok:
        raise HTTPException(404, "Item not found")
    return {"message": "Deleted"}


# ══════════════════════════════════════════════════════════════
# الخدمات
# ══════════════════════════════════════════════════════════════

@app.get("/api/services", tags=["Services"])
async def get_services(_: bool = Depends(verify_token)):
    return await db.get_services()


@app.post("/api/services", tags=["Services"])
async def create_service(
    name: str, price_range: str, icon: str = "🤖",
    description: str = "", _: bool = Depends(verify_token)
):
    sid = await db.add_service(name, price_range, icon, description)
    if not sid:
        raise HTTPException(500, "Failed to add service")
    return {"message": "Created", "id": sid}


@app.delete("/api/services/{service_id}", tags=["Services"])
async def delete_service(service_id: int, _: bool = Depends(verify_token)):
    ok = await db.delete_service(service_id)
    if not ok:
        raise HTTPException(404, "Service not found")
    return {"message": "Deleted"}


# ══════════════════════════════════════════════════════════════
# الإحصائيات
# ══════════════════════════════════════════════════════════════

@app.get("/api/stats", tags=["Stats"])
async def get_stats(_: bool = Depends(verify_token)):
    return await db.get_dashboard_stats()


@app.get("/api/stats/weekly", tags=["Stats"])
async def get_weekly(_: bool = Depends(verify_token)):
    return await db.get_weekly_orders()


@app.get("/api/stats/monthly", tags=["Stats"])
async def get_monthly(_: bool = Depends(verify_token)):
    return await db.get_monthly_stats()


# ══════════════════════════════════════════════════════════════
# البث عبر API
# ══════════════════════════════════════════════════════════════

@app.post("/api/broadcast", tags=["Admin"])
async def api_broadcast(message: str, _: bool = Depends(verify_token)):
    if not bot_instance:
        raise HTTPException(503, "Bot not ready")
    user_ids = await db.get_all_user_ids()
    sent, failed = 0, 0
    for uid in user_ids:
        try:
            await bot_instance.send_message(uid, message, parse_mode="HTML")
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1
    await db.log_broadcast(message, sent, config.ADMIN_ID)
    return {"sent": sent, "failed": failed, "total": len(user_ids)}


# ══════════════════════════════════════════════════════════════
# تشغيل
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=config.PORT,
        reload=False,
        log_level="info",
    )
