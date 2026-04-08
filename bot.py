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
🌟 <b>أهلاً وسهلاً بك في {COMPANY_NAME}</b> 🌟
━━━━━━━━━━━━━━━━━━━━

👋 <b>مرحباً:</b> {message.from_user.first_name}
🏢 <b>شركة {COMPANY_NAME}</b>
👨‍💼 <b>المدير التنفيذي:</b> {CEO_NAME}

💎 <b>لماذا تختارنا؟</b>
✅ أسعار منافسة وجودة عالية
✅ تسليم سريع وضمان حقيقي
✅ دعم فني 24/7
✅ طرق دفع متعددة ومرنة

🎁 <b>عروض خاصة:</b>
🔸 خصم 10% للطلب الأول
🔸 خصم 15% عند مشاركة البوت
🔸 نقاط ولاء على كل طلب
🔸 هدايا حصرية للمشتركين

📢 <b>تابعنا على القناة:</b> {CHANNEL_LINK}
"""
    
    if not is_subscribed:
        welcome_text += f"""

⚠️ <b>ملاحظة مهمة:</b>
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
🎯 <b>خدمات {COMPANY_NAME} المتكاملة</b>
━━━━━━━━━━━━━━━━━━━━

🤖 <b>بوتات تلجرام:</b> من 100$
📱 <b>تطبيقات الجوال:</b> من 500$
💻 <b>مواقع إلكترونية:</b> من 200$
🛒 <b>متاجر إلكترونية:</b> من 400$
🔧 <b>معاملات برمجية:</b> من 150$
🎨 <b>خدمات مميزة:</b> من 50$

📞 <b>للطلب:</b> اضغط 'طلب جديد'
👨‍💼 <b>المدير:</b> {ADMIN_USERNAME}
"""
    await message.answer(text, reply_markup=services_inline_kb(), parse_mode="HTML")

async def payment_handler(message: types.Message):
    text = f"""
💳 <b>طرق الدفع المتاحة</b>
━━━━━━━━━━━━━━━━━━━━

🌍 <b>اختر دولتك لعرض طرق الدفع:</b>

🇾🇪 <b>اليمن:</b>
   • البنوك اليمنية (الكريمي، تضامن...)
   • المحافظ الإلكترونية (جيب، جوالي...)

🌍 <b>دول أخرى:</b>
   • باي بال (PayPal)
   • ويسترن يونيون
   • تحويل بنكي دولي
   • USDT (Crypto)

📝 <b>ملاحظات مهمة:</b>
• يتم إرسال تفاصيل الدفع بعد تأكيد الطلب
• يحتفظ بالإيصال بعد التحويل
• يتم تفعيل الطلب خلال 24 ساعة
• الحد الأدنى للطلب: 50$

💡 <b>لبدء الطلب:</b> اضغط 'طلب جديد'

👨‍💼 <b>للاستفسار:</b> {ADMIN_USERNAME}
"""
    await message.answer(text, reply_markup=country_selection_kb(), parse_mode="HTML")

# ==================== معالج الأعمال (Portfolio) المحدث ====================
async def portfolio_handler(message: types.Message):
    text = f"""
📁 <b>أعمال {COMPANY_NAME}</b>
━━━━━━━━━━━━━━━━━━━━

🎨 <b>نماذج من مشاريعنا:</b>

🤖 <b>البوتات:</b>
• بوت متجر إلكتروني - 150$
• بوت حماية متقدم - 200$
• بوت خدمة عملاء - 180$

📱 <b>التطبيقات:</b>
• تطبيق توصيل طلبات - 800$
• تطبيق إدارة مهام - 650$
• تطبيق متجر - 950$

💻 <b>المواقع:</b>
• موقع شركة - 350$
• موقع متجر - 550$
• موقع خدمات - 400$

🛒 <b>المتاجر:</b>
• متجر إلكتروني كامل - 750$
• متجر مع بوت - 900$

📌 <b>اختر نوع المشروع لعرض التفاصيل:</b>
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
👤 <b>معلومات حسابك</b>
━━━━━━━━━━━━━━━━━━━━

📊 <b>الإحصائيات:</b>
├ إجمالي الطلبات: {len(orders)}
├ الطلبات النشطة: {pending}
├ الطلبات المكتملة: {completed}
└ نقاط الولاء: {points} 🪙

🎁 <b>مزاياك:</b>
├ خصم متاح: {discount_percent}%
└ الرصيد: {points * 0.1}$ (قابل للاستخدام)

📦 <b>آخر طلباتك:</b>
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
│ {status_emoji} <b>طلب #{order['id']}</b>
│ ├ الخدمة: {order['service_type']}
│ ├ الميزانية: {order['budget']}
│ └ التاريخ: {date_str}
└────────────────
"""
    else:
        text += "\n❌ <b>لا توجد طلبات بعد</b>\n🎁 ابدأ بطلبك الأول واحصل على خصم 10%!"
    
    text += f"""

💡 <b>استخدم نقاطك:</b>
• كل 10 نقاط = خصم 1$
• شارك البوت واربح 50 نقطة
• اطلب واحصل على نقاط

👨‍💼 <b>المدير:</b> {ADMIN_USERNAME}
📢 <b>القناة:</b> {CHANNEL_LINK}
"""
    
    await message.answer(text, parse_mode="HTML")

async def order_handler(message: types.Message, state: FSMContext):
    await state.set_state(OrderState.service_type)
    
    text = f"""
📝 <b>بدء طلب جديد - {COMPANY_NAME}</b>
━━━━━━━━━━━━━━━━━━━━

🎯 <b>اختر نوع الخدمة:</b>

💡 نصيحة: اختر الخدمة الأنسب لمشروعك
👨‍💼 للاستفسار: {ADMIN_USERNAME}
"""
    await message.answer(text, reply_markup=services_inline_kb(), parse_mode="HTML")

async def support_handler(message: types.Message):
    text = f"""
💬 <b>الدعم الفني - {COMPANY_NAME}</b>
━━━━━━━━━━━━━━━━━━━━

👨‍💼 <b>فريقنا جاهز لمساعدتك!</b>

📞 <b>التواصل المباشر:</b>
├ الدعم الفني: {SUPPORT_USERNAME}
└ المدير التنفيذي: {ADMIN_USERNAME}

⏱ <b>وقت الاستجابة:</b>
├ خلال 24 ساعة للتذاكر
└ فوري للدعم المباشر

🎫 <b>نظام التذاكر:</b>
• تتبع طلباتك
• محادثة منظمة
• حفظ السجل

❓ <b>الأسئلة الشائعة:</b>
• إجابات سريعة
• حلول فورية

💡 نحن هنا لمساعدتك 24/7!

📢 تابعنا: {CHANNEL_LINK}
"""
    await message.answer(text, reply_markup=support_kb(), parse_mode="HTML")

async def contact_admin(message: types.Message):
    text = f"""
📞 <b>تواصل مع الإدارة</b>
━━━━━━━━━━━━━━━━━━━━

👨‍💼 <b>المدير التنفيذي:</b> {CEO_NAME}
📱 <b>الحساب:</b> {ADMIN_USERNAME}

💡 <b>متى تتواصل؟</b>
• للاستفسارات المهمة
• للمشاريع الكبيرة
• للشكاوى والاقتراحات
• للاستشارات المجانية

⏱ <b>متوفر:</b> 9 صباحاً - 11 مساءً

🔗 <b>اضغط هنا للتواصل:</b>
https://t.me/{ADMIN_USERNAME.replace('@', '')}

📢 <b>القناة الرسمية:</b> {CHANNEL_LINK}
"""
    await message.answer(text, parse_mode="HTML")

async def share_handler(message: types.Message):
    user = await db.get_user(message.from_user.id)
    points = user['loyalty_points'] if user else 0
    
    text = f"""
🤝 <b>شارك واربح - {COMPANY_NAME}</b>
━━━━━━━━━━━━━━━━━━━━

🎁 <b>برنامج الإحالة:</b>

💰 <b>كيف تربح؟</b>
1️⃣ شارك البوت مع أصدقائك
2️⃣ احصل على 50 نقطة لكل صديق
3️⃣ استبدل النقاط بخصومات!

🎯 <b>المكافآت:</b>
• 50 نقطة = خصم 5$
• 100 نقطة = خصم 10$
• 200 نقطة = خصم 25$ + هدية

📊 <b>رصيدك الحالي:</b> {points} نقطة
💵 <b>القيمة:</b> {points * 0.1}$

📤 <b>شارك الآن:</b>
اضغط الزر أدناه لمشاركة البوت

📢 <b>لا تنسى الانضمام للقناة:</b>
{CHANNEL_LINK}

👨‍💼 <b>المدير:</b> {ADMIN_USERNAME}
"""
    await message.answer(text, reply_markup=share_kb(), parse_mode="HTML")

async def offers_handler(message: types.Message):
    text = f"""
🎁 <b>العروض والهدايا - {COMPANY_NAME}</b>
━━━━━━━━━━━━━━━━━━━━

🔥 <b>العروض الحالية:</b>

🎉 <b>عرض الطلب الأول:</b>
• خصم 10% على أول طلب
• الكود: FIRST10
• ساري دائماً

🎊 <b>عرض الباقة الكاملة:</b>
• موقع + بوت + تطبيق
• خصم 25%
• الكود: VEXO25

🏆 <b>برنامج الولاء:</b>
• اجمع نقاط مع كل طلب
• استبدلها بخصومات
• هدايا حصرية

🎟️ <b>كوبونات الخصم:</b>
• FIRST10 = 10% (للطلب الأول)
• VEXO15 = 15% (للطلبات فوق 300$)
• SHARE20 = 20% (بعد مشاركة البوت)
• VIP25 = 25% (للطلبات فوق 1000$)

💡 <b>استخدم الكود عند الطلب!</b>

👨‍💼 <b>المدير:</b> {ADMIN_USERNAME}
📢 <b>القناة:</b> {CHANNEL_LINK}
"""
    await message.answer(text, reply_markup=offers_kb(), parse_mode="HTML")

async def callback_handler(call: types.CallbackQuery, state: FSMContext):
    data = call.data
    
    if data == "main_menu":
        await call.message.edit_text("📋 <b>القائمة الرئيسية:</b>", reply_markup=main_keyboard(), parse_mode="HTML")
    
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
            f"📝 <b>أرسل تفاصيل المشروع:</b>\n"
            f"• ما الوظيفة المطلوبة؟\n"
            f"• ما الميزات الخاصة؟\n"
            f"• هل هناك متطلبات إضافية؟",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]]),
            parse_mode="HTML"
        )
    
    # اختيار الدولة
    elif data == "country_yemen":
        await call.message.edit_text(
            "🇾🇪 <b>اليمن - طرق الدفع</b>\n\n"
            "💳 <b>اختر طريقة الدفع:</b>",
            reply_markup=yemen_payment_kb(),
            parse_mode="HTML"
        )
    
    elif data == "country_other":
        await call.message.edit_text(
            "🌍 <b>دول أخرى - طرق الدفع</b>\n\n"
            "💳 <b>اختر طريقة الدفع الدولية:</b>",
            reply_markup=international_payment_kb(),
            parse_mode="HTML"
        )
    
    # البنوك اليمنية
    elif data == "yemen_banks":
        await call.message.edit_text(
            "🏦 <b>البنوك اليمنية</b>\n\n"
            "📋 <b>اختر البنك:</b>\n\n"
            "💡 ملاحظة: سيتم إرسال رقم الحساب بعد تأكيد الطلب",
            reply_markup=yemen_banks_kb(),
            parse_mode="HTML"
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
            f"📝 <b>سيتم إرسال رقم الحساب</b>\n"
            f"بعد تأكيد طلبك\n\n"
            f"💡 <b>لبدء الطلب:</b> اضغط 'طلب جديد'",
            reply_markup=yemen_banks_kb(),
            parse_mode="HTML"
        )
    
    # المحافظ اليمنية
    elif data == "yemen_wallets":
        await call.message.edit_text(
            "📱 <b>المحافظ الإلكترونية - اليمن</b>\n\n"
            "💳 <b>اختر المحفظة:</b>",
            reply_markup=yemen_wallets_kb(),
            parse_mode="HTML"
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
            f"📝 <b>سيتم إرسال رقم المحفظة</b>\n"
            f"بعد تأكيد طلبك\n\n"
            f"💡 <b>لبدء الطلب:</b> اضغط 'طلب جديد'",
            reply_markup=yemen_wallets_kb(),
            parse_mode="HTML"
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
            f"📝 <b>سيتم إرسال تفاصيل الدفع</b>\n"
            f"بعد تأكيد طلبك\n\n"
            f"⏱ <b>التفعيل:</b> 24-48 ساعة\n\n"
            f"💡 <b>لبدء الطلب:</b> اضغط 'طلب جديد'",
            reply_markup=international_payment_kb(),
            parse_mode="HTML"
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
                f"✅ <b>تم استلام طلبك بنجاح!</b>\n\n"
                f"🎉 <b>تهانينا!</b> حصلت على 10 نقاط ولاء\n\n"
                f"📦 <b>تفاصيل الطلب:</b>\n"
                f"├ رقم الطلب: #{order_id}\n"
                f"├ الخدمة: {data_state.get('service_type')}\n"
                f"├ الميزانية: {budget_map[data]}\n"
                f"└ التفاصيل: {data_state.get('details')[:100]}...\n\n"
                f"🔔 <b>سيتم مراجعته خلال 24 ساعة</b>\n"
                f"💡 <b>تابع حسابك لمعرفة التحديثات</b>\n\n"
                f"👨‍💼 <b>المدير:</b> {ADMIN_USERNAME}",
                reply_markup=main_keyboard(),
                parse_mode="HTML"
            )
            
            try:
                await call.message.bot.send_message(
                    config.ADMIN_ID,
                    f"🔔 <b>طلب جديد!</b>\n\n"
                    f"👤 المستخدم: {call.from_user.username or call.from_user.first_name}\n"
                    f"🆔 ID: {call.from_user.id}\n"
                    f"📦 الخدمة: {data_state.get('service_type')}\n"
                    f"💰 الميزانية: {budget_map[data]}\n"
                    f"📝 التفاصيل: {data_state.get('details')}",
                    parse_mode="HTML"
                )
            except:
                pass
    
    # الدعم الفني
    elif data == "ticket_new":
        await state.set_state(SupportState.message)
        await call.message.edit_text(
            "🎫 <b>فتح تذكرة دعم جديدة</b>\n\n"
            "📝 <b>اكتب مشكلتك بالتفصيل:</b>\n"
            "• ما المشكلة؟\n"
            "• متى ظهرت؟\n"
            "• ما الخطوات التي جربتها؟",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 إلغاء", callback_data="main_menu")]]),
            parse_mode="HTML"
        )
    
    elif data == "ticket_my":
        tickets = await db.get_user_tickets(call.from_user.id)
        if tickets:
            text = "📋 <b>تذاكرك السابقة:</b>\n\n"
            for ticket in tickets[:5]:
                status_emoji = "🟢" if ticket['status'] == 'closed' else "🟡"
                text += f"{status_emoji} تذكرة #{ticket['id']} - {ticket['status']}\n"
            await call.message.edit_text(text, reply_markup=support_kb(), parse_mode="HTML")
        else:
            await call.message.edit_text("📋 <b>لا توجد تذاكر سابقة</b>", reply_markup=support_kb(), parse_mode="HTML")
    
    elif data == "faq":
        faq_text = f"""
❓ <b>الأسئلة الشائعة - {COMPANY_NAME}</b>
━━━━━━━━━━━━━━━━━━━━

<b>س: كم وقت التنفيذ؟</b>
ج: 3-7 أيام للبوتات، 7-14 يوم للتطبيقات

<b>س: هل هناك ضمان؟</b>
ج: نعم، ضمان 30 يوم على جميع المشاريع

<b>س: طرق الدفع؟</b>
ج: محافظ محلية (جيب، ون كاش...) وبنوك يمنية ودولية

<b>س: هل هناك دعم بعد التسليم؟</b>
ج: نعم، دعم مجاني لمدة شهر

<b>س: كيف أطلب؟</b>
ج: اضغط 'طلب جديد' واتبع الخطوات

<b>س: هل يمكن التعديل بعد التسليم؟</b>
ج: نعم، بسعر مناسب حسب التعديل

<b>س: كيف أربح نقاط؟</b>
ج: اطلب، شارك البوت، احصل على مكافآت

👨‍💼 <b>للاستفسار:</b> {ADMIN_USERNAME}
📢 <b>القناة:</b> {CHANNEL_LINK}
"""
        await call.message.edit_text(faq_text, reply_markup=support_kb(), parse_mode="HTML")
    
    # العروض
    elif data == "offers_current":
        await call.message.edit_text(
            "🔥 <b>العروض الحالية</b>\n\n"
            "🎉 <b>عرض الطلب الأول:</b> 10% خصم\n"
            "🎊 <b>الباقة الكاملة:</b> 25% خصم\n"
            "🏆 <b>الطلبات الكبيرة:</b> خصم حتى 30%\n\n"
            "💡 <b>استخدم الكود عند الطلب!</b>",
            reply_markup=offers_kb(),
            parse_mode="HTML"
        )
    
    elif data == "offers_coupons":
        await call.message.edit_text(
            "🎟️ <b>كوبونات الخصم</b>\n\n"
            "FIRST10 = 10% (الطلب الأول)\n"
            "VEXO15 = 15% (فوق 300$)\n"
            "SHARE20 = 20% (بعد المشاركة)\n"
            "VIP25 = 25% (فوق 1000$)\n\n"
            "💡 <b>اطلب الكود من المدير</b>",
            reply_markup=offers_kb(),
            parse_mode="HTML"
        )
    
    elif data == "offers_loyalty":
        await call.message.edit_text(
            "🏆 <b>برنامج الولاء</b>\n\n"
            "💰 <b>كيف يعمل؟</b>\n"
            "• كل طلب = 10-50 نقطة\n"
            "• كل مشاركة = 50 نقطة\n"
            "• كل 10 نقاط = 1$ خصم\n\n"
            "🎁 <b>مستويات الولاء:</b>\n"
            "🥉 برونزي: 0-100 نقطة\n"
            "🥈 فضي: 100-500 نقطة\n"
            "🥇 ذهبي: 500+ نقطة\n\n"
            "💎 <b>مزايا الذهب:</b> خصم إضافي 5%",
            reply_markup=offers_kb(),
            parse_mode="HTML"
        )
    
    elif data == "offers_seasonal":
        await call.message.edit_text(
            "🎪 <b>عروض موسمية</b>\n\n"
            "🎄 <b>عرض العيد:</b> 20% خصم\n"
            "🎓 <b>عرض الطلاب:</b> 15% خصم\n"
            "🎂 <b>عرض السنة الجديدة:</b> قريباً\n\n"
            "📢 <b>تابعنا للعروض الجديدة!</b>",
            reply_markup=offers_kb(),
            parse_mode="HTML"
        )
    
    elif data == "share_claim":
        user = await db.get_user(call.from_user.id)
        points = user['loyalty_points'] if user else 0
        
        await call.message.edit_text(
            f"🎁 <b>رصيدك من النقاط:</b> {points}\n\n"
            f"💰 <b>القيمة:</b> {points * 0.1}$\n\n"
            f"📤 <b>شارك الآن واربح 50 نقطة!</b>\n"
            f"🔗 رابط البوت: @VexoServiceBot\n\n"
            f"📢 <b>لا تنسى الانضمام للقناة:</b>\n{CHANNEL_LINK}",
            reply_markup=share_kb(),
            parse_mode="HTML"
        )
    
    elif data == "share_leaderboard":
        await call.message.edit_text(
            "🏆 <b>صدارة المشاركين</b>\n\n"
            "🥇 المستخدم الأول: 500 نقطة\n"
            "🥈 المستخدم الثاني: 350 نقطة\n"
            "🥉 المستخدم الثالث: 200 نقطة\n\n"
            "📊 <b>أنت:</b> شارك لتظهر هنا!",
            reply_markup=share_kb(),
            parse_mode="HTML"
        )
    
    # ==================== الأعمال (Portfolio) المحدث ====================
    elif data == "port_bot":
        projects = await db.get_portfolio("bot")
        if projects:
            text = "🤖 <b>مشاريع البوتات:</b>\n\n"
            for proj in projects[:5]:
                text += f"┌────────────────\n"
                text += f"│ <b>{proj['title']}</b>\n"
                if proj.get('price'):
                    text += f"│ 💰 السعر: {proj['price']}\n"
                if proj.get('description'):
                    desc = proj['description'][:150]
                    text += f"│ 📝 {desc}{'...' if len(proj['description']) > 150 else ''}\n"
                if proj.get('features'):
                    text += f"│ ⭐ الميزات: {proj['features']}\n"
                if proj.get('preview_link'):
                    text += f"│ 🔗 <a href='{proj['preview_link']}'>معاينة</a>\n"
                text += f"└────────────────\n\n"
            await call.message.edit_text(text, reply_markup=portfolio_kb(), parse_mode="HTML")
        else:
            await call.message.edit_text("🤖 <b>مشاريع البوتات:</b>\n\n📌 قريباً...", reply_markup=portfolio_kb(), parse_mode="HTML")
    
    elif data == "port_app":
        projects = await db.get_portfolio("app")
        if projects:
            text = "📱 <b>مشاريع التطبيقات:</b>\n\n"
            for proj in projects[:5]:
                text += f"┌────────────────\n"
                text += f"│ <b>{proj['title']}</b>\n"
                if proj.get('price'):
                    text += f"│ 💰 السعر: {proj['price']}\n"
                if proj.get('description'):
                    desc = proj['description'][:150]
                    text += f"│ 📝 {desc}{'...' if len(proj['description']) > 150 else ''}\n"
                if proj.get('features'):
                    text += f"│ ⭐ الميزات: {proj['features']}\n"
                if proj.get('preview_link'):
                    text += f"│ 🔗 <a href='{proj['preview_link']}'>معاينة</a>\n"
                text += f"└────────────────\n\n"
            await call.message.edit_text(text, reply_markup=portfolio_kb(), parse_mode="HTML")
        else:
            await call.message.edit_text("📱 <b>مشاريع التطبيقات:</b>\n\n📌 قريباً...", reply_markup=portfolio_kb(), parse_mode="HTML")
    
    elif data == "port_web":
        projects = await db.get_portfolio("web")
        if projects:
            text = "💻 <b>مشاريع المواقع:</b>\n\n"
            for proj in projects[:5]:
                text += f"┌────────────────\n"
                text += f"│ <b>{proj['title']}</b>\n"
                if proj.get('price'):
                    text += f"│ 💰 السعر: {proj['price']}\n"
                if proj.get('description'):
                    desc = proj['description'][:150]
                    text += f"│ 📝 {desc}{'...' if len(proj['description']) > 150 else ''}\n"
                if proj.get('features'):
                    text += f"│ ⭐ الميزات: {proj['features']}\n"
                if proj.get('preview_link'):
                    text += f"│ 🔗 <a href='{proj['preview_link']}'>معاينة</a>\n"
                text += f"└────────────────\n\n"
            await call.message.edit_text(text, reply_markup=portfolio_kb(), parse_mode="HTML")
        else:
            await call.message.edit_text("💻 <b>مشاريع المواقع:</b>\n\n📌 قريباً...", reply_markup=portfolio_kb(), parse_mode="HTML")
    
    elif data == "port_store":
        projects = await db.get_portfolio("store")
        if projects:
            text = "🛒 <b>مشاريع المتاجر:</b>\n\n"
            for proj in projects[:5]:
                text += f"┌────────────────\n"
                text += f"│ <b>{proj['title']}</b>\n"
                if proj.get('price'):
                    text += f"│ 💰 السعر: {proj['price']}\n"
                if proj.get('description'):
                    desc = proj['description'][:150]
                    text += f"│ 📝 {desc}{'...' if len(proj['description']) > 150 else ''}\n"
                if proj.get('features'):
                    text += f"│ ⭐ الميزات: {proj['features']}\n"
                if proj.get('preview_link'):
                    text += f"│ 🔗 <a href='{proj['preview_link']}'>معاينة</a>\n"
                text += f"└────────────────\n\n"
            await call.message.edit_text(text, reply_markup=portfolio_kb(), parse_mode="HTML")
        else:
            await call.message.edit_text("🛒 <b>مشاريع المتاجر:</b>\n\n📌 قريباً...", reply_markup=portfolio_kb(), parse_mode="HTML")
    
    elif data == "port_all":
        projects = await db.get_portfolio()
        if projects:
            text = "📚 <b>جميع المشاريع:</b>\n\n"
            for proj in projects[:10]:
                type_emoji = {"bot": "🤖", "app": "📱", "web": "💻", "store": "🛒"}.get(proj['type'], "📁")
                text += f"{type_emoji} <b>{proj['title']}</b> ({proj['type']})\n"
                if proj.get('price'):
                    text += f"   💰 {proj['price']}\n"
                if proj.get('description'):
                    text += f"   📝 {proj['description'][:100]}...\n"
                text += "\n"
            await call.message.edit_text(text, reply_markup=portfolio_kb(), parse_mode="HTML")
        else:
            await call.message.edit_text("📚 <b>جميع المشاريع:</b>\n\n📌 قريباً...", reply_markup=portfolio_kb(), parse_mode="HTML")
    
    await call.answer()

async def handle_order_details(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state == OrderState.details:
        await state.update_data(details=message.text)
        await state.set_state(OrderState.budget)
        await message.answer(
            "💰 <b>اختر الميزانية المتوقعة:</b>\n\n"
            "💡 نصيحة: اختر الميزانية الأقرب لمشروعك",
            reply_markup=budget_kb(),
            parse_mode="HTML"
        )
    
    elif current_state == SupportState.message:
        ticket_id = await db.create_ticket(message.from_user.id, message.text)
        await state.clear()
        
        await message.answer(
            f"✅ <b>تم فتح تذكرة الدعم!</b>\n\n"
            f"🎫 رقم التذكرة: #{ticket_id}\n"
            f"📝 رسالتك: {message.text[:100]}...\n\n"
            f"⏱ <b>سنرد عليك خلال 24 ساعة</b>\n"
            f"💬 <b>للتواصل السريع:</b> {SUPPORT_USERNAME}\n"
            f"👨‍💼 <b>المدير:</b> {ADMIN_USERNAME}",
            reply_markup=main_keyboard(),
            parse_mode="HTML"
        )
        
        try:
            await message.bot.send_message(
                config.ADMIN_ID,
                f"🎫 <b>تذكرة دعم جديدة!</b>\n\n"
                f"👤 المستخدم: {message.from_user.username or message.from_user.first_name}\n"
                f"🆔 ID: {message.from_user.id}\n"
                f"🎫 الرقم: #{ticket_id}\n"
                f"📝 الرسالة: {message.text}",
                parse_mode="HTML"
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
