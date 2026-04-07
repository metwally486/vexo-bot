from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import config
import database as db

# الأزرار الرئيسية
main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🛠 خدماتنا"), KeyboardButton(text="📝 اطلب الآن")],
    [KeyboardButton(text="👤 حسابي"), KeyboardButton(text="💬 دعم فني")]
], resize_keyboard=True)

# --- المعالجات (Handlers) ---

async def start_handler(message: types.Message):
    await db.add_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await message.answer(
        f"أهلاً بك يا {message.from_user.first_name}! 👋\nأنا بوت Vexo للخدمات التقنية.",
        reply_markup=main_kb
    )

async def services_handler(message: types.Message):
    await message.answer("🛠 **خدماتنا:**\n🤖 بوتات تلجرام\n📱 تطبيقات جوال\n💻 مواقع ويب")

async def profile_handler(message: types.Message):
    orders = await db.get_user_orders(message.from_user.id)
    text = f"👤 **حسابك**\n📊 عدد الطلبات: {len(orders)}"
    await message.answer(text, parse_mode="Markdown")

async def order_handler(message: types.Message):
    await message.answer("📝 لطلب خدمة، أرسل تفاصيل مشروعك والميزانية.")

async def support_handler(message: types.Message):
    await message.answer(f"💬 للدعم الفني تواصل مع المالك: @{config.ADMIN_ID}")

async def handle_text(message: types.Message):
    order_id = await db.create_order(message.from_user.id, "عام", message.text, "غير محدد")
    await message.answer(f"✅ تم استلام طلبك رقم #{order_id}")
    try:
        await message.bot.send_message(config.ADMIN_ID, f"🔔 طلب جديد من {message.from_user.first_name}:\n{message.text}")
    except: pass

# --- دالة التسجيل (التصحيح هنا) ---

def register_handlers(dp: Dispatcher):
    dp.message.register(start_handler, Command("start"))
    dp.message.register(services_handler, F.text == "🛠 خدماتنا")
    dp.message.register(profile_handler, F.text == "👤 حسابي")
    dp.message.register(order_handler, F.text == "📝 اطلب الآن")
    dp.message.register(support_handler, F.text == "💬 دعم فني")
    dp.message.register(handle_text) # يجب أن يكون الأخير
    dp.message.register(support_handler, F.text == "💬 دعم فني")
    dp.message.register(handle_text)
