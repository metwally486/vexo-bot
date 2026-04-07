from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
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
    
    # إيقاف التشغيل - تصحيح: استخدام bot.close() بدلاً من bot.session.close()
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

# التحقق من المفتاح (تأكد من وجود API_SECRET_KEY في config.py)
async def verify_token(x_api_key: str = Header(None)):
    if not hasattr(config, 'API_SECRET_KEY') or x_api_key != config.API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return True

# نقاط API
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
