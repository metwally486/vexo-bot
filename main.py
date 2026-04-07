from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import os
import uvicorn
import config
import database as db
from bot import register_handlers
from aiogram import Bot, Dispatcher

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. تهيئة قاعدة البيانات
    await db.init_db()
    
    # 2. إعداد البوت
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    register_handlers(dp)
    
    # 3. تشغيل البوت في الخلفية (Polling)
    polling_task = asyncio.create_task(dp.start_polling(bot))
    print("Vexo Bot is starting...")
    
    yield
    
    # 4. إغلاق الجلسات عند التوقف
    polling_task.cancel()
    await bot.session.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "running", "service": "Vexo-Bot API"}

# تشغيل السيرفر بالمنفذ الصحيح لـ Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
