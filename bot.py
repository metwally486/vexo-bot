from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import config
import database as db
from datetime import datetime

# ==================== معلومات الشركة ====================
COMPANY_NAME = "Vexo للخدمات التقنية"
CEO_NAME = "متولي الوصابي"
ADMIN_USERNAME = "@m_7_1_1_w"  # المدير
SUPPORT_USERNAME = "@abohamed12"  # الدعم الفني
CHANNEL_LINK = "https://t.me/abod_IT"
CHANNEL_USERNAME = "abod_IT"

# ==================== حالات النموذج ====================

class OrderState(StatesGroup):
    service_type = State()
    details = State()
    budget = State()

class SupportState(StatesGroup):
    message = State()

class PortfolioState(StatesGroup):
    title = State()
    project_type = State()
    description = State()
    preview_link = State()

# ==================== الأزرار الرئيسية ====================

def main_keyboard():
    kb = [
        [KeyboardButton(text="🎯 خدماتنا"), KeyboardButton(text="📝 طلب جديد")],
        [KeyboardButton(text="🎁 العروض والهدايا"), KeyboardButton(text="💳 طرق الدفع")],
        [KeyboardButton(text="📁 أعمالنا"), KeyboardButton(text="👤 حسابي")],
        [KeyboardButton(text="🤝 شارك واريح"), KeyboardButton(text="💬 الدعم الفني")],
        [KeyboardButton(text="تواصل مع الإدارة")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def services_inline_kb():
    kb = [
        [InlineKeyboardButton(text="🤖 إنشاء بوت تلجرام", callback_data="srv_create_bot")],
        [InlineKeyboardButton(text="⚙️ تطوير بوت موجود", callback_data="srv_dev_bot")],
        [InlineKeyboardButton(text="📱 تطبيق أندرويد", callback_data="srv_android")],
        [InlineKeyboardButton(text="🍎 تطبيق iOS", callback_data="srv_ios")],
        [InlineKeyboardButton(text="💻 موقع إلكتروني", callback_data="srv_website")],
        [InlineKeyboardButton(text="🛒 متجر إلكتروني", callback_data="srv_store")],
        [InlineKeyboardButton(text="🔧 معاملات برمجية", callback_data="srv_scripts")],
        [InlineKeyboardButton(text="🎨 خدمات مميزة", callback_data="srv_premium")],
        [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def country_selection_kb():
    kb = [
        [InlineKeyboardButton(text="🇾🇪 اليمن", callback_data="country_yemen")],
        [InlineKeyboardButton(text="🌍 دولة أخرى", callback_data="country_other")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def yemen_payment_kb():
    kb = [
        [InlineKeyboardButton(text="🏦 البنوك اليمنية", callback_data="yemen_banks")],
        [InlineKeyboardButton(text="📱 المحافظ الإلكترونية", callback_data="yemen_wallets")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def yemen_banks_kb():
    kb = [
        [InlineKeyboardButton(text="💰 الكريمي", callback_data="bank_kareemi")],
        [InlineKeyboardButton(text="🤝 تضامن", callback_data="bank_tadhamon")],
        [InlineKeyboardButton(text="🏛 بنك اليمن والكويت", callback_data="bank_yemen_kuwait")],
        [InlineKeyboardButton(text="🏦 البنك الأهلي", callback_data="bank_ahli")],
        [InlineKeyboardButton(text="🏦 بنك صنعاء", callback_data="bank_sanaa")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def yemen_wallets_kb():
    kb = [
        [InlineKeyboardButton(text="📱 جيب (Jeew)", callback_data="wallet_jeew")],
        [InlineKeyboardButton(text="📲 جوالي (Jawali)", callback_data="wallet_jawali")],
        [InlineKeyboardButton(text="💵 ون كاش (OneCash)", callback_data="wallet_onecash")],
        [InlineKeyboardButton(text="💰 موني (Monee)", callback_data="wallet_monee")],
        [InlineKeyboardButton(text="💳 فلوسك (Floosak)", callback_data="wallet_floosak")],
        [InlineKeyboardButton(text="📱 عمرون (Omran)", callback_data="wallet_omran")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def international_payment_kb():
    kb = [
        [InlineKeyboardButton(text="💳 باي بال (PayPal)", callback_data="intl_paypal")],
        [InlineKeyboardButton(text="💵 ويسترن يونيون", callback_data="intl_western")],
        [InlineKeyboardButton(text="🏦 تحويل بنكي", callback_data="intl_bank")],
        [InlineKeyboardButton(text="💰 USDT (Crypto)", callback_data="intl_usdt")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def budget_kb():
    kb = [
        [InlineKeyboardButton(text="💰 أقل من 100$", callback_data="budget_low")],
        [InlineKeyboardButton(text="💵 100$ - 300$", callback_data="budget_mid")],
        [InlineKeyboardButton(text="💎 300$ - 1000$", callback_data="budget_high")],
        [InlineKeyboardButton(text="👑 أكثر من 1000$", callback_data="budget_premium")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def support_kb():
    kb = [
        [InlineKeyboardButton(text="🎫 فتح تذكرة جديدة", callback_data="ticket_new")],
        [InlineKeyboardButton(text="📋 تذاكري السابقة", callback_data="ticket_my")],
        [InlineKeyboardButton(text="❓ الأسئلة الشائعة", callback_data="faq")],
        [InlineKeyboardButton(text="👨‍💻 الدعم الفني", url=f"https://t.me/{SUPPORT_USERNAME.replace('@', '')}")],
        [InlineKeyboardButton(text="📞 المدير التنفيذي", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def portfolio_kb():
    kb = [
        [InlineKeyboardButton(text="🤖 البوتات", callback_data="port_bot")],
        [InlineKeyboardButton(text="📱 التطبيقات", callback_data="port_app")],
        [InlineKeyboardButton(text="💻 المواقع", callback_data="port_web")],
        [InlineKeyboardButton(text="🛒 المتاجر", callback_data="port_store")],
        [InlineKeyboardButton(text="📚 الكل", callback_data="port_all")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def share_kb():
    kb = [
        [InlineKeyboardButton(text="📤 مشاركة البوت", switch_inline_query=f"🎉 انضم لي على {COMPANY_NAME} للخدمات التقنية! 🚀\n\n🔗 الرابط: @VexoServiceBot")],
        [InlineKeyboardButton(text="🎁 استلام الهدية", callback_data="share_claim")],
        [InlineKeyboardButton(text="🏆 صدارة المشاركين", callback_data="share_leaderboard")],
        [InlineKeyboardButton(text="📢 الانضمام للقناة", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def offers_kb():
    kb = [
        [InlineKeyboardButton(text="🎁 العروض الحالية", callback_data="offers_current")],
        [InlineKeyboardButton(text="🎟️ كوبونات الخصم", callback_data="offers_coupons")],
        [InlineKeyboardButton(text="🏆 برنامج الولاء", callback_data="offers_loyalty")],
        [InlineKeyboardButton(text="🎪 عروض موسمية", callback_data="offers_seasonal")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def admin_portfolio_kb():
    kb = [
        [InlineKeyboardButton(text="➕ إضافة مشروع", callback_data="portfolio_add")],
        [InlineKeyboardButton(text="📋 عرض المشاريع", callback_data="portfolio_list")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

# ==================== المعالجات ====================

async def check_channel_subscription(message: types.Message) -> bool:
    """التحقق من اشتراك المستخدم في القناة"""
    try:
        member = await message.bot.get_chat_member(CHANNEL_USERNAME, message.from_user.id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

async def start_handler(message: types.Message):
    await db.add_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    
    is_subscribed = await check_channel_subscription(message)
    
    welcome_text = f"""
🌟 **أهلاً وسهلاً بك في {COMPANY_NAME}** 🌟
━━━━━━━━━━━━━━━━━━━━

👋 **مرحباً:** {message.from_user.first_name}
🏢 **شركة {COMPANY_NAME}**
👨‍💼 **المدير التنفيذي:** {CEO_NAME}

💎 **لماذا تختارنا؟**
✅ أسعار منافسة وجودة عالية
✅ تسليم سريع وضمان حقيقي
✅ دعم فني 24/7
✅ طرق دفع متعددة ومرنة

🎁 **عروض خاصة:**
🔸 خصم 10% للطلب الأول
🔸 خصم 15% عند مشاركة البوت
🔸 نقاط ولاء على كل طلب
🔸 هدايا حصرية للمشتركين

📢 **تابعنا على القناة:** {CHANNEL_LINK}
"""
    
    if not is_subscribed:
        welcome_text += f"""

⚠️ **ملاحظة مهمة:**
للحصول على جميع المزايا والهدايا، يرجى الانضمام لقناتنا أولاً:
{CHANNEL_LINK}
"""
    
    await message.answer(
        welcome_text,
        reply_markup=main_keyboard(),
        parse_mode="HTML"
    )

async def services_handler(message: types.Message):
    text = f"""
🎯 **خدمات {COMPANY_NAME} المتكاملة**
━━━━━━━━━━━━━━━━━━━━

🤖 **بوتات تلجرام:**
   • إنشاء بوتات متاجر إلكترونية
   • بوتات حماية وإدارة المجموعات
   • بوتات خدمة عملاء ذكية
   • بوتات مخصصة حسب الطلب
   💰 من 100$

📱 **تطبيقات الجوال:**
   • تطبيقات أندرويد احترافية
   • تطبيقات iOS (آيفون)
   • مع لوحة تحكم كاملة
   💰 من 500$

💻 **المواقع الإلكترونية:**
   • مواقع متاجر متكاملة
   • مواقع تعريفية للشركات
   • لوحات إدارة متطورة
   💰 من 200$

🛒 **المتاجر الإلكترونية:**
   • متاجر كاملة مع بوت
   • أنظمة دفع متعددة
   • إدارة مخزون وطلبات
   💰 من 400$

🔧 **معاملات برمجية:**
   • سكربتات مخصصة
   • أتمتة المهام
   • تكامل APIs
   💰 من 150$

🎨 **خدمات مميزة:**
   • تصميم شعارات
   • هوية بصرية
   • تسويق إلكتروني
   💰 من 50$

📞 **للطلب:** اضغط 'طلب جديد'
👨‍💼 **المدير:** {ADMIN_USERNAME}
"""
    await message.answer(text, reply_markup=services_inline_kb(), parse_mode="HTML")

async def payment_handler(message: types.Message):
    text = f"""
💳 **طرق الدفع المتاحة**
━━━━━━━━━━━━━━━━━━━━

🌍 **اختر دولتك لعرض طرق الدفع:**

🇾🇪 **اليمن:**
   • البنوك اليمنية (الكريمي، تضامن...)
   • المحافظ الإلكترونية (جيب، جوالي...)

🌍 **دول أخرى:**
   • باي بال (PayPal)
   • ويسترن يونيون
   • تحويل بنكي دولي
   • USDT (Crypto)

📝 **ملاحظات مهمة:**
• يتم إرسال تفاصيل الدفع بعد تأكيد الطلب
• يحتفظ بالإيصال بعد التحويل
• يتم تفعيل الطلب خلال 24 ساعة
• الحد الأدنى للطلب: 50$

💡 **لبدء الطلب:** اضغط 'طلب جديد'

👨‍💼 **للاستفسار:** {ADMIN_USERNAME}
"""
    await message.answer(text, reply_markup=country_selection_kb(), parse_mode="HTML")

async def portfolio_handler(message: types.Message):
    text = f"""
📁 **أعمال {COMPANY_NAME}**
━━━━━━━━━━━━━━━━━━━━

🎨 **نماذج من مشاريعنا:**

🤖 **البوتات:**
• بوت متجر إلكتروني - 150$
• بوت حماية متقدم - 200$
• بوت خدمة عملاء - 180$

📱 **التطبيقات:**
• تطبيق توصيل طلبات - 800$
• تطبيق إدارة مهام - 650$
• تطبيق متجر - 950$

💻 **المواقع:**
• موقع شركة - 350$
• موقع متجر - 550$
• موقع خدمات - 400$

🛒 **المتاجر:**
• متجر إلكتروني كامل - 750$
• متجر مع بوت - 900$

📌 **اختر نوع المشروع:**
"""
    await message.answer(text, reply_markup=portfolio_kb(), parse_mode="HTML")

async def profile_handler(message: types.Message):
    user = await db.get_user(message.from_user.id)
    orders = await db.get_user_orders(message.from_user.id)
    
    points = user['loyalty_points'] if user else 0
    discount_percent = min(points // 10, 25)
    
    completed = len([o for o in orders if o['status'] == 'completed'])
    pending = len([o for o in orders if o['status'] in ['pending', 'processing']])
    
    text = f"""
👤 **معلومات حسابك**
━━━━━━━━━━━━━━━━━━━━

📊 **الإحصائيات:**
├ إجمالي الطلبات: {len(orders)}
├ الطلبات النشطة: {pending}
├ الطلبات المكتملة: {completed}
└ نقاط الولاء: {points} 🪙

🎁 **مزاياك:**
├ خصم متاح: {discount_percent}%
└ الرصيد: {points * 0.1}$ (قابل للاستخدام)

📦 **آخر طلباتك:**
"""
    
    if orders:
        for order in orders[:5]:
            status_emoji = {
                "pending": "⏳ قيد المراجعة",
                "processing": "🔄 قيد التنفيذ", 
                "completed": "✅ مكتمل",
                "rejected": "❌ مرفوض"
            }.get(order['status'], "⏳")
            
            date_str = "N/A"
            if hasattr(order.get('created_at'), 'strftime'):
                date_str = order['created_at'].strftime('%Y-%m-%d')
            elif order.get('created_at'):
                date_str = str(order['created_at'])[:10]
            
            text += f"""
┌────────────────
│ {status_emoji} **طلب #{order['id']}**
│ ├ الخدمة: {order['service_type']}
│ ├ الميزانية: {order['budget']}
│ └ التاريخ: {date_str}
└────────────────
"""
    else:
        text += "\n❌ **لا توجد طلبات بعد**\n🎁 ابدأ بطلبك الأول واحصل على خصم 10%!"
    
    text += f"""

💡 **استخدم نقاطك:**
• كل 10 نقاط = خصم 1$
• شارك البوت واربح 50 نقطة
• اطلب واحصل على نقاط

👨‍💼 **المدير:** {ADMIN_USERNAME}
📢 **القناة:** {CHANNEL_LINK}
"""
    
    await message.answer(text, parse_mode="HTML")

async def order_handler(message: types.Message, state: FSMContext):
    await state.set_state(OrderState.service_type)
    
    text = f"""
📝 **بدء طلب جديد - {COMPANY_NAME}**
━━━━━━━━━━━━━━━━━━━━

🎯 **اختر نوع الخدمة:**

💡 **نصيحة:** اختر الخدمة الأنسب لمشروعك
👨‍💼 **للاستفسار:** {ADMIN_USERNAME}
"""
    await message.answer(text, reply_markup=services_inline_kb(), parse_mode="HTML")

async def support_handler(message: types.Message):
    text = f"""
💬 **الدعم الفني - {COMPANY_NAME}**
━━━━━━━━━━━━━━━━━━━━

👨‍💼 **فريقنا جاهز لمساعدتك!**

📞 **التواصل المباشر:**
├ الدعم الفني: {SUPPORT_USERNAME}
└ المدير التنفيذي: {ADMIN_USERNAME}

⏱ **وقت الاستجابة:**
├ خلال 24 ساعة للتذاكر
└ فوري للدعم المباشر

🎫 **نظام التذاكر:**
• تتبع طلباتك
• محادثة منظمة
• حفظ السجل

❓ **الأسئلة الشائعة:**
• إجابات سريعة
• حلول فورية

💡 **نحن هنا لمساعدتك 24/7!**

📢 **تابعنا:** {CHANNEL_LINK}
"""
    await message.answer(text, reply_markup=support_kb(), parse_mode="HTML")

async def contact_admin(message: types.Message):
    text = f"""
📞 **تواصل مع الإدارة**
━━━━━━━━━━━━━━━━━━━━

👨‍💼 **المدير التنفيذي:** {CEO_NAME}
📱 **الحساب:** {ADMIN_USERNAME}

💡 **متى تتواصل؟**
• للاستفسارات المهمة
• للمشاريع الكبيرة
• للشكاوى والاقتراحات
• للاستشارات المجانية

⏱ **متوفر:** 9 صباحاً - 11 مساءً

🔗 **اضغط هنا للتواصل:**
https://t.me/{ADMIN_USERNAME.replace('@', '')}

📢 **القناة الرسمية:** {CHANNEL_LINK}
"""
    await message.answer(text, parse_mode="HTML")

async def share_handler(message: types.Message):
    user = await db.get_user(message.from_user.id)
    points = user['loyalty_points'] if user else 0
    
    text = f"""
🤝 **شارك واربح - {COMPANY_NAME}**
━━━━━━━━━━━━━━━━━━━━

🎁 **برنامج الإحالة:**

💰 **كيف تربح؟**
1️⃣ شارك البوت مع أصدقائك
2️⃣ احصل على 50 نقطة لكل صديق
3️⃣ استبدل النقاط بخصومات!

🎯 **المكافآت:**
• 50 نقطة = خصم 5$
• 100 نقطة = خصم 10$
• 200 نقطة = خصم 25$ + هدية

📊 **رصيدك الحالي:** {points} نقطة
💵 **القيمة:** {points * 0.1}$

📤 **شارك الآن:**
اضغط الزر أدناه لمشاركة البوت

📢 **لا تنسى الانضمام للقناة:**
{CHANNEL_LINK}

👨‍💼 **المدير:** {ADMIN_USERNAME}
"""
    await message.answer(text, reply_markup=share_kb(), parse_mode="HTML")

async def offers_handler(message: types.Message):
    text = f"""
🎁 **العروض والهدايا - {COMPANY_NAME}**
━━━━━━━━━━━━━━━━━━━━

🔥 **العروض الحالية:**

🎉 **عرض الطلب الأول:**
• خصم 10% على أول طلب
• الكود: FIRST10
• ساري دائماً

🎊 **عرض الباقة الكاملة:**
• موقع + بوت + تطبيق
• خصم 25%
• الكود: VEXO25

🏆 **برنامج الولاء:**
• اجمع نقاط مع كل طلب
• استبدلها بخصومات
• هدايا حصرية

🎟️ **كوبونات الخصم:**
• FIRST10 = 10% (للطلب الأول)
• VEXO15 = 15% (للطلبات فوق 300$)
• SHARE20 = 20% (بعد مشاركة البوت)
• VIP25 = 25% (للطلبات فوق 1000$)

💡 **استخدم الكود عند الطلب!**

👨‍💼 **المدير:** {ADMIN_USERNAME}
📢 **القناة:** {CHANNEL_LINK}
"""
    await message.answer(text, reply_markup=offers_kb(), parse_mode="HTML")

async def callback_handler(call: types.CallbackQuery, state: FSMContext):
    data = call.data
    
    if data == "main_menu":
        await call.message.edit_text("📋 **القائمة الرئيسية:**", reply_markup=main_keyboard())
    
    # خدمات
    elif data.startswith("srv_"):
        service_map = {
            "srv_create_bot": "🤖 إنشاء بوت تلجرام",
            "srv_dev_bot": "⚙️ تطوير بوت موجود",
            "srv_android": "📱 تطبيق أندرويد",
            "srv_ios": "🍎 تطبيق iOS",
            "srv_website": "💻 موقع إلكتروني",
            "srv_store": "🛒 متجر إلكتروني",
            "srv_scripts": "🔧 معاملات برمجية",
            "srv_premium": "🎨 خدمات مميزة"
        }
        service_name = service_map.get(data, "خدمة")
        await state.update_data(service_type=service_name)
        await state.set_state(OrderState.details)
        await call.message.edit_text(
            f"✅ {service_name}\n\n"
            f"📝 **أرسل تفاصيل المشروع:**\n"
            f"• ما الوظيفة المطلوبة؟\n"
            f"• ما الميزات الخاصة؟\n"
            f"• هل هناك متطلبات إضافية؟",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]])
        )
    
    # اختيار الدولة
    elif data == "country_yemen":
        await call.message.edit_text(
            "🇾🇪 **اليمن - طرق الدفع**\n\n"
            "💳 **اختر طريقة الدفع:**",
            reply_markup=yemen_payment_kb()
        )
    
    elif data == "country_other":
        await call.message.edit_text(
            "🌍 **دول أخرى - طرق الدفع**\n\n"
            "💳 **اختر طريقة الدفع الدولية:**",
            reply_markup=international_payment_kb()
        )
    
    # البنوك اليمنية
    elif data == "yemen_banks":
        await call.message.edit_text(
            "🏦 **البنوك اليمنية**\n\n"
            "📋 **اختر البنك:**\n\n"
            "💡 **ملاحظة:** سيتم إرسال رقم الحساب بعد تأكيد الطلب",
            reply_markup=yemen_banks_kb()
        )
    
    elif data.startswith("bank_"):
        bank_map = {
            "bank_kareemi": "💰 الكريمي",
            "bank_tadhamon": "🤝 تضامن",
            "bank_yemen_kuwait": "🏛 بنك اليمن والكويت",
            "bank_ahli": "🏦 البنك الأهلي",
            "bank_sanaa": "🏦 بنك صنعاء"
        }
        bank_name = bank_map.get(data, "البنك")
        await call.message.edit_text(
            f"✅ {bank_name}\n\n"
            f"📝 **سيتم إرسال رقم الحساب**\n"
            f"بعد تأكيد طلبك\n\n"
            f"💡 **لبدء الطلب:** اضغط 'طلب جديد'",
            reply_markup=yemen_banks_kb()
        )
    
    # المحافظ اليمنية
    elif data == "yemen_wallets":
        await call.message.edit_text(
            "📱 **المحافظ الإلكترونية - اليمن**\n\n"
            "💳 **اختر المحفظة:**",
            reply_markup=yemen_wallets_kb()
        )
    
    elif data.startswith("wallet_"):
        wallet_map = {
            "wallet_jeew": "📱 جيب (Jeew)",
            "wallet_jawali": "📲 جوالي (Jawali)",
            "wallet_onecash": "💵 ون كاش (OneCash)",
            "wallet_monee": "💰 موني (Monee)",
            "wallet_floosak": "💳 فلوسك (Floosak)",
            "wallet_omran": "📱 عمرون (Omran)"
        }
        wallet_name = wallet_map.get(data, "المحفظة")
        await call.message.edit_text(
            f"✅ {wallet_name}\n\n"
            f"📝 **سيتم إرسال رقم المحفظة**\n"
            f"بعد تأكيد طلبك\n\n"
            f"💡 **لبدء الطلب:** اضغط 'طلب جديد'",
            reply_markup=yemen_wallets_kb()
        )
    
    # الدفع الدولي
    elif data.startswith("intl_"):
        intl_map = {
            "intl_paypal": "💳 باي بال (PayPal)",
            "intl_western": "💵 ويسترن يونيون",
            "intl_bank": "🏦 تحويل بنكي",
            "intl_usdt": "💰 USDT (Crypto)"
        }
        method_name = intl_map.get(data, "الطريقة")
        await call.message.edit_text(
            f"✅ {method_name}\n\n"
            f"📝 **سيتم إرسال تفاصيل الدفع**\n"
            f"بعد تأكيد طلبك\n\n"
            f"⏱ **التفعيل:** 24-48 ساعة\n\n"
            f"💡 **لبدء الطلب:** اضغط 'طلب جديد'",
            reply_markup=international_payment_kb()
        )
    
    # الميزانية
    elif data.startswith("budget_"):
        budget_map = {
            "budget_low": "أقل من 100$",
            "budget_mid": "100$ - 300$",
            "budget_high": "300$ - 1000$",
            "budget_premium": "أكثر من 1000$"
        }
        await state.update_data(budget=budget_map[data])
        
        data_state = await state.get_data()
        order_id = await db.create_order(
            user_id=call.from_user.id,
            service_type=data_state.get("service_type", "عام"),
            details=data_state.get("details", ""),
            budget=budget_map[data]
        )
        
        if order_id:
            await db.add_points(call.from_user.id, 10)
            await state.clear()
            
            await call.message.edit_text(
                f"✅ **تم استلام طلبك بنجاح!**\n\n"
                f"🎉 **تهانينا!** حصلت على 10 نقاط ولاء\n\n"
                f"📦 **تفاصيل الطلب:**\n"
                f"├ رقم الطلب: #{order_id}\n"
                f"├ الخدمة: {data_state.get('service_type')}\n"
                f"├ الميزانية: {budget_map[data]}\n"
                f"└ التفاصيل: {data_state.get('details')[:100]}...\n\n"
                f"🔔 **سيتم مراجعته خلال 24 ساعة**\n"
                f"💡 **تابع حسابك لمعرفة التحديثات**\n\n"
                f"👨‍💼 **المدير:** {ADMIN_USERNAME}",
                reply_markup=main_keyboard()
            )
            
            try:
                await call.message.bot.send_message(
                    config.ADMIN_ID,
                    f"🔔 **طلب جديد!**\n\n"
                    f"👤 المستخدم: {call.from_user.username or call.from_user.first_name}\n"
                    f"🆔 ID: {call.from_user.id}\n"
                    f"📦 الخدمة: {data_state.get('service_type')}\n"
                    f"💰 الميزانية: {budget_map[data]}\n"
                    f"📝 التفاصيل: {data_state.get('details')}"
                )
            except:
                pass
    
    # الدعم الفني
    elif data == "ticket_new":
        await state.set_state(SupportState.message)
        await call.message.edit_text(
            "🎫 **فتح تذكرة دعم جديدة**\n\n"
            "📝 **اكتب مشكلتك بالتفصيل:**\n"
            "• ما المشكلة؟\n"
            "• متى ظهرت؟\n"
            "• ما الخطوات التي جربتها؟",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 إلغاء", callback_data="main_menu")]])
        )
    
    elif data == "ticket_my":
        tickets = await db.get_user_tickets(call.from_user.id)
        if tickets:
            text = "📋 **تذاكرك السابقة:**\n\n"
            for ticket in tickets[:5]:
                status_emoji = "🟢" if ticket['status'] == 'closed' else "🟡"
                text += f"{status_emoji} تذكرة #{ticket['id']} - {ticket['status']}\n"
            await call.message.edit_text(text, reply_markup=support_kb())
        else:
            await call.message.edit_text("📋 **لا توجد تذاكر سابقة**", reply_markup=support_kb())
    
    elif data == "faq":
        faq_text = f"""
❓ **الأسئلة الشائعة - {COMPANY_NAME}**
━━━━━━━━━━━━━━━━━━━━

**س: كم وقت التنفيذ؟**
ج: 3-7 أيام للبوتات، 7-14 يوم للتطبيقات

**س: هل هناك ضمان؟**
ج: نعم، ضمان 30 يوم على جميع المشاريع

**س: طرق الدفع؟**
ج: محافظ محلية (جيب، ون كاش...) وبنوك يمنية ودولية

**س: هل هناك دعم بعد التسليم؟**
ج: نعم، دعم مجاني لمدة شهر

**س: كيف أطلب؟**
ج: اضغط 'طلب جديد' واتبع الخطوات

**س: هل يمكن التعديل بعد التسليم؟**
ج: نعم، بسعر مناسب حسب التعديل

**س: كيف أربح نقاط؟**
ج: اطلب، شارك البوت، احصل على مكافآت

👨‍💼 **للاستفسار:** {ADMIN_USERNAME}
📢 **القناة:** {CHANNEL_LINK}
"""
        await call.message.edit_text(faq_text, reply_markup=support_kb())
    
    # العروض
    elif data == "offers_current":
        await call.message.edit_text(
            "🔥 **العروض الحالية**\n\n"
            "🎉 **عرض الطلب الأول:** 10% خصم\n"
            "🎊 **الباقة الكاملة:** 25% خصم\n"
            "🏆 **الطلبات الكبيرة:** خصم حتى 30%\n\n"
            "💡 **استخدم الكود عند الطلب!**",
            reply_markup=offers_kb()
        )
    
    elif data == "offers_coupons":
        await call.message.edit_text(
            "🎟️ **كوبونات الخصم**\n\n"
            "FIRST10 = 10% (الطلب الأول)\n"
            "VEXO15 = 15% (فوق 300$)\n"
            "SHARE20 = 20% (بعد المشاركة)\n"
            "VIP25 = 25% (فوق 1000$)\n\n"
            "💡 **اطلب الكود من المدير**",
            reply_markup=offers_kb()
        )
    
    elif data == "offers_loyalty":
        await call.message.edit_text(
            "🏆 **برنامج الولاء**\n\n"
            "💰 **كيف يعمل؟**\n"
            "• كل طلب = 10-50 نقطة\n"
            "• كل مشاركة = 50 نقطة\n"
            "• كل 10 نقاط = 1$ خصم\n\n"
            "🎁 **مستويات الولاء:**\n"
            "🥉 برونزي: 0-100 نقطة\n"
            "🥈 فضي: 100-500 نقطة\n"
            "🥇 ذهبي: 500+ نقطة\n\n"
            "💎 **مزايا الذهب:** خصم إضافي 5%",
            reply_markup=offers_kb()
        )
    
    elif data == "offers_seasonal":
        await call.message.edit_text(
            "🎪 **عروض موسمية**\n\n"
            "🎄 **عرض العيد:** 20% خصم\n"
            "🎓 **عرض الطلاب:** 15% خصم\n"
            "🎂 **عرض السنة الجديدة:** قريباً\n\n"
            "📢 **تابعنا للعروض الجديدة!**",
            reply_markup=offers_kb()
        )
    
    elif data == "share_claim":
        user = await db.get_user(call.from_user.id)
        points = user['loyalty_points'] if user else 0
        
        await call.message.edit_text(
            f"🎁 **رصيدك من النقاط:** {points}\n\n"
            f"💰 **القيمة:** {points * 0.1}$\n\n"
            f"📤 **شارك الآن واربح 50 نقطة!**\n"
            f"🔗 رابط البوت: @VexoServiceBot\n\n"
            f"📢 **لا تنسى الانضمام للقناة:**\n{CHANNEL_LINK}",
            reply_markup=share_kb()
        )
    
    elif data == "share_leaderboard":
        await call.message.edit_text(
            "🏆 **صدارة المشاركين**\n\n"
            "🥇 المستخدم الأول: 500 نقطة\n"
            "🥈 المستخدم الثاني: 350 نقطة\n"
            "🥉 المستخدم الثالث: 200 نقطة\n\n"
            "📊 **أنت:** شارك لتظهر هنا!",
            reply_markup=share_kb()
        )
    
    # الأعمال (Portfolio)
    elif data == "port_bot":
        projects = await db.get_portfolio("bot")
        if projects:
            text = "🤖 **مشاريع البوتات:**\n\n"
            for proj in projects[:3]:
                text += f"• **{proj['title']}**\n"
                if proj.get('description'):
                    text += f"  {proj['description'][:100]}\n"
                text += "\n"
            await call.message.edit_text(text, reply_markup=portfolio_kb())
        else:
            await call.message.edit_text("🤖 **مشاريع البوتات:**\n\n📌 قريباً...", reply_markup=portfolio_kb())
    
    elif data == "port_app":
        projects = await db.get_portfolio("app")
        if projects:
            text = "📱 **مشاريع التطبيقات:**\n\n"
            for proj in projects[:3]:
                text += f"• **{proj['title']}**\n"
                if proj.get('description'):
                    text += f"  {proj['description'][:100]}\n"
                text += "\n"
            await call.message.edit_text(text, reply_markup=portfolio_kb())
        else:
            await call.message.edit_text("📱 **مشاريع التطبيقات:**\n\n📌 قريباً...", reply_markup=portfolio_kb())
    
    elif data == "port_web":
        projects = await db.get_portfolio("web")
        if projects:
            text = "💻 **مشاريع المواقع:**\n\n"
            for proj in projects[:3]:
                text += f"• **{proj['title']}**\n"
                if proj.get('description'):
                    text += f"  {proj['description'][:100]}\n"
                text += "\n"
            await call.message.edit_text(text, reply_markup=portfolio_kb())
        else:
            await call.message.edit_text("💻 **مشاريع المواقع:**\n\n📌 قريباً...", reply_markup=portfolio_kb())
    
    elif data == "port_store":
        projects = await db.get_portfolio("store")
        if projects:
            text = "🛒 **مشاريع المتاجر:**\n\n"
            for proj in projects[:3]:
                text += f"• **{proj['title']}**\n"
                if proj.get('description'):
                    text += f"  {proj['description'][:100]}\n"
                text += "\n"
            await call.message.edit_text(text, reply_markup=portfolio_kb())
        else:
            await call.message.edit_text("🛒 **مشاريع المتاجر:**\n\n📌 قريباً...", reply_markup=portfolio_kb())
    
    elif data == "port_all":
        projects = await db.get_portfolio()
        if projects:
            text = "📚 **جميع المشاريع:**\n\n"
            for proj in projects[:5]:
                text += f"• **{proj['title']}** ({proj['type']})\n"
                if proj.get('description'):
                    text += f"  {proj['description'][:100]}\n"
                text += "\n"
            await call.message.edit_text(text, reply_markup=portfolio_kb())
        else:
            await call.message.edit_text("📚 **جميع المشاريع:**\n\n📌 قريباً...", reply_markup=portfolio_kb())
    
    await call.answer()

async def handle_order_details(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state == OrderState.details:
        await state.update_data(details=message.text)
        await state.set_state(OrderState.budget)
        await message.answer(
            "💰 **اختر الميزانية المتوقعة:**\n\n"
            "💡 **نصيحة:** اختر الميزانية الأقرب لمشروعك",
            reply_markup=budget_kb()
        )
    
    elif current_state == SupportState.message:
        ticket_id = await db.create_ticket(message.from_user.id, message.text)
        await state.clear()
        
        await message.answer(
            f"✅ **تم فتح تذكرة الدعم!**\n\n"
            f"🎫 رقم التذكرة: #{ticket_id}\n"
            f"📝 رسالتك: {message.text[:100]}...\n\n"
            f"⏱ **سنرد عليك خلال 24 ساعة**\n"
            f"💬 **للتواصل السريع:** {SUPPORT_USERNAME}\n"
            f"👨‍💼 **المدير:** {ADMIN_USERNAME}",
            reply_markup=main_keyboard()
        )
        
        try:
            await message.bot.send_message(
                config.ADMIN_ID,
                f"🎫 **تذكرة دعم جديدة!**\n\n"
                f"👤 المستخدم: {message.from_user.username or message.from_user.first_name}\n"
                f"🆔 ID: {message.from_user.id}\n"
                f"🎫 الرقم: #{ticket_id}\n"
                f"📝 الرسالة: {message.text}"
            )
        except:
            pass

def register_handlers(dp: Dispatcher):
    dp.message.register(start_handler, Command("start"))
    dp.message.register(services_handler, F.text == "🎯 خدماتنا")
    dp.message.register(portfolio_handler, F.text == "📁 أعمالنا")
    dp.message.register(profile_handler, F.text == "👤 حسابي")
    dp.message.register(order_handler, F.text == "📝 طلب جديد")
    dp.message.register(support_handler, F.text == "💬 الدعم الفني")
    dp.message.register(payment_handler, F.text == "💳 طرق الدفع")
    dp.message.register(contact_admin, F.text == "تواصل مع الإدارة")
    dp.message.register(share_handler, F.text == "🤝 شارك واريح")
    dp.message.register(offers_handler, F.text == "🎁 العروض والهدايا")
    
    dp.message.register(handle_order_details, ~F.text.in_([
        "🎯 خدماتنا", "📁 أعمالنا", "👤 حسابي", "📝 طلب جديد",
        "💬 الدعم الفني", "💳 طرق الدفع", "تواصل مع الإدارة",
        "🤝 شارك واريح", "🎁 العروض والهدايا"
    ]))
    
    dp.callback_query.register(callback_handler)
