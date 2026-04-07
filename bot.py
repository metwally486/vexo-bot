from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import config
import database as db

# الأزرار الرئيسية
main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🛠 خدماتنا"), KeyboardButton(text="📝 اطلب الآن")],
    [KeyboardButton(text="👤 حسابي"), KeyboardButton(text="💬 دعم فني")]
], resize_keyboard=True)

# معالج /start
async def start_handler(message: types.Message):
    await db.add_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    await message.answer(
        f"أهلاً بك يا {message.from_user.first_name}! 👋\n\n"
        f"أنا بوت Vexo للخدمات التقنية.\n"
        f"كيف يمكننا مساعدتك اليوم؟",
        reply_markup=main_kb
    )

# معالج الخدمات
async def services_handler(message: types.Message):
    await message.answer(
        "🛠 **خدماتنا:**\n\n"
        "🤖 **بوتات تلجرام**\n"
        "📱 **تطبيقات جوال**\n"
        "💻 **مواقع ويب**\n\n"
        "لطلب أي خدمة، اضغط على 'اطلب الآن'"
    )

# معالج حسابي
async def profile_handler(message: types.Message):
    user = await db.get_user(message.from_user.id)
    orders = await db.get_user_orders(message.from_user.id)
    
    text = f"👤 **حسابك**\n\n"
    text += f"📊 عدد الطلبات: {len(orders)}\n\n"
    
    if orders:
        text += "📦 **طلباتك:**\n"
        for order in orders[:5]:  # آخر 5 طلبات
            status_emoji = {"pending": "⏳", "processing": "🔄", "completed": "✅", "rejected": "❌"}.get(order['status'], "⏳")
            text += f"{status_emoji} {order['service_type']} - {order['status']}\n"
    
    await message.answer(text, parse_mode="Markdown")

# معالج اطلب الآن
async def order_handler(message: types.Message):    await message.answer(
        "📝 **لطلب خدمة، أرسل لي:**\n\n"
        "1️⃣ نوع الخدمة (بوت/تطبيق/موقع)\n"
        "2️⃣ تفاصيل المشروع\n"
        "3️⃣ الميزانية المتوقعة\n\n"
        "**مثال:**\n"
        "بوت تلجرام لمتجر إلكتروني\n"
        "الميزانية: 200$\n"
        "التفاصيل: إدارة منتجات، دفع، إشعارات"
    )

# معالج الدعم الفني
async def support_handler(message: types.Message):
    await message.answer(
        "💬 **الدعم الفني**\n\n"
        "للتواصل المباشر:\n"
        f"👤 المالك: @{config.ADMIN_ID}\n\n"
        "أو أرسل مشكلتك هنا وسنقوم بفتح تذكرة دعم."
    )

# معالج الرسائل النصية (للطلبات)
async def handle_text(message: types.Message):
    text = message.text
    
    # حفظ الطلب
    order_id = await db.create_order(
        user_id=message.from_user.id,
        service_type="عام",
        details=text,
        budget="غير محدد"
    )
    
    await message.answer(
        f"✅ **تم استلام طلبك!**\n\n"
        f"رقم الطلب: #{order_id}\n"
        f"سيقوم المدير بمراجعته قريباً."
    )
    
    # إشعار للمدير
    try:
        await message.bot.send_message(
            config.ADMIN_ID,
            f"🔔 **طلب جديد!**\n\n"
            f"👤 المستخدم: {message.from_user.username or message.from_user.first_name}\n"
            f"📝 الطلب:\n{text}"
        )
    except:
        pass

# تسجيل المعالجاتdef register_handlers(dp: Dispatcher):
    dp.message.register(start_handler, Command("start"))
    dp.message.register(services_handler, F.text == "🛠 خدماتنا")
    dp.message.register(profile_handler, F.text == "👤 حسابي")
    dp.message.register(order_handler, F.text == "📝 اطلب الآن")
    dp.message.register(support_handler, F.text == "💬 دعم فني")
    dp.message.register(handle_text)
