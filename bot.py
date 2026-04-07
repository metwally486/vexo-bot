from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import config
import database as db

# الأزرار
main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🛠 خدماتنا"), KeyboardButton(text="📝 اطلب الآن")],
    [KeyboardButton(text="👤 حسابي"), KeyboardButton(text="💬 دعم فني")]
], resize_keyboard=True)

async def start_handler(message: types.Message):
    await db.add_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await message.answer(f"أهلاً بك! 👋\nأنا بوت Vexo.", reply_markup=main_kb)

async def services_handler(message: types.Message):
    await message.answer("🛠 خدماتنا:\n🤖 بوتات\n📱 تطبيقات\n مواقع")

async def profile_handler(message: types.Message):
    orders = await db.get_user_orders(message.from_user.id)
    text = f"📦 طلباتك: {len(orders)}\n"
    for o in orders[:3]:
        text += f"- {o['service_type']} ({o['status']})\n"
    await message.answer(text if text else "لا توجد طلبات")

async def order_handler(message: types.Message):
    await message.answer("📝 أرسل تفاصيل طلبك:")

async def support_handler(message: types.Message):
    await message.answer("💬 للدعم: تواصل مع المدير")

async def handle_text(message: types.Message):
    await db.create_order(message.from_user.id, "عام", message.text, "غير محدد")
    await message.answer("✅ تم استلام طلبك!")
    try:
        await message.bot.send_message(config.ADMIN_ID, f"🔔 طلب جديد:\n{message.text}")
    except: pass

def register_handlers(dp: Dispatcher):
    dp.message.register(start_handler, Command("start"))
    dp.message.register(services_handler, F.text == "🛠 خدماتنا")
    dp.message.register(profile_handler, F.text == "👤 حسابي")
    dp.message.register(order_handler, F.text == "📝 اطلب الآن")
    dp.message.register(support_handler, F.text == "💬 دعم فني")
    dp.message.register(handle_text)
