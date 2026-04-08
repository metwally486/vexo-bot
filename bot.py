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
ADMIN_USERNAME = "@m_7_1_1_w"
SUPPORT_USERNAME = "@abohamed12"
CHANNEL_LINK = "https://t.me/abod_IT"
CHANNEL_USERNAME = "abod_IT"

# ==================== حالات النموذج ====================

class OrderState(StatesGroup):
    service_type = State()
    details = State()
    budget = State()
    payment_method = State()
    confirm = State()

class SupportState(StatesGroup):
    message = State()

# ==================== الأزرار ====================

def main_keyboard():
    kb = [
        [KeyboardButton(text="🎯 خدماتنا"), KeyboardButton(text="📝 طلب جديد")],
        [KeyboardButton(text="🎁 العروض والهدايا"), KeyboardButton(text="💳 طرق الدفع")],
        [KeyboardButton(text="📁 أعمالنا"), KeyboardButton(text="👤 حسابي")],
        [KeyboardButton(text="🤝 شارك واربح"), KeyboardButton(text="💬 الدعم الفني")],
        [KeyboardButton(text="📞 الإدارة")]
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
        [InlineKeyboardButton(text="🔧 معاملات برمجية", callback_data="srv_scripts")],        [InlineKeyboardButton(text="🎨 خدمات مميزة", callback_data="srv_premium")],
        [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def payment_methods_kb():
    kb = [
        [InlineKeyboardButton(text="📱 جيب (Jeew)", callback_data="pay_jeew")],
        [InlineKeyboardButton(text="📲 جوالي (Jawali)", callback_data="pay_jawali")],
        [InlineKeyboardButton(text="💵 ون كاش (OneCash)", callback_data="pay_onecash")],
        [InlineKeyboardButton(text="💰 موني (Monee)", callback_data="pay_monee")],
        [InlineKeyboardButton(text="💳 فلوسك (Floosak)", callback_data="pay_floosak")],
        [InlineKeyboardButton(text="💰 الكريمي", callback_data="pay_kareemi")],
        [InlineKeyboardButton(text="🤝 تضامن", callback_data="pay_tadhamon")],
        [InlineKeyboardButton(text="🏛 بنك اليمن والكويت", callback_data="pay_yemen_kuwait")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def confirmation_kb():
    kb = [
        [InlineKeyboardButton(text="✅ تأكيد الطلب", callback_data="order_confirm")],
        [InlineKeyboardButton(text="❌ إلغاء", callback_data="order_cancel")]
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
        [InlineKeyboardButton(text="🤖 البوتات", callback_data="port_bot")],        [InlineKeyboardButton(text="📱 التطبيقات", callback_data="port_app")],
        [InlineKeyboardButton(text="💻 المواقع", callback_data="port_web")],
        [InlineKeyboardButton(text="🛒 المتاجر", callback_data="port_store")],
        [InlineKeyboardButton(text="📚 الكل", callback_data="port_all")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def share_kb():
    kb = [
        [InlineKeyboardButton(text="📤 مشاركة البوت", switch_inline_query=f"🎉 انضم لي على {COMPANY_NAME} للخدمات التقنية! 🚀\n\n🔗 الرابط: @VexoServiceBot")],
        [InlineKeyboardButton(text="📢 الانضمام للقناة", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="🎁 استلام الهدية", callback_data="share_claim")],
        [InlineKeyboardButton(text="🏆 صدارة المشاركين", callback_data="share_leaderboard")],
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

# ==================== دوال مساعدة ====================

async def check_channel_subscription(user_id: int, bot: Bot) -> bool:
    """التحقق من اشتراك المستخدم في القناة"""
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

async def add_share_points(user_id: int) -> bool:
    """إضافة نقاط للمشاركة (50 نقطة)"""
    return await db.add_points(user_id, 50)

async def add_join_points(user_id: int) -> bool:
    """إضافة نقاط للانضمام للقناة (30 نقطة)"""
    return await db.add_points(user_id, 30)

# ==================== المعالجات ====================

async def start_handler(message: types.Message):
    await db.add_user(message.from_user.id, message.from_user.username, message.from_user.full_name)    
    is_subscribed = await check_channel_subscription(message.from_user.id, message.bot)
    
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

📢 **تابعنا:** {CHANNEL_LINK}
"""
    
    if not is_subscribed:
        welcome_text += f"""

⚠️ **انضم لقناتنا واحصل على 30 نقطة!**
{CHANNEL_LINK}
"""
    
    await message.answer(
        welcome_text,
        reply_markup=main_keyboard(),
        parse_mode="Markdown"
    )

async def services_handler(message: types.Message):
    text = f"""
🎯 **خدمات {COMPANY_NAME} المتكاملة**
━━━━━━━━━━━━━━━━━━━━

🤖 **بوتات تلجرام:**
   • إنشاء بوتات متاجر إلكترونية
   • بوتات حماية وإدارة المجموعات
   • بوتات خدمة عملاء ذكية
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

📞 **للطلب:** اضغط 'طلب جديد'
"""
    await message.answer(text, reply_markup=services_inline_kb(), parse_mode="Markdown")

async def payment_handler(message: types.Message):
    text = f"""
💳 **طرق الدفع المتاحة - {COMPANY_NAME}**
━━━━━━━━━━━━━━━━━━━━

📱 **المحافظ الإلكترونية:**
• جيب (Jeew)
• جوالي (Jawali)
• ون كاش (OneCash)
• موني (Monee)
• فلوسك (Floosak)

🏦 **البنوك اليمنية:**
• الكريمي
• تضامن
• بنك اليمن والكويت

📝 **ملاحظات مهمة:**
• يتم إرسال رقم الحساب/المحفظة بعد تأكيد الطلب
• يحتفظ بالإيصال بعد التحويل
• يتم تفعيل الطلب خلال 24 ساعة

💡 **اختر طريقة الدفع المفضلة:**
"""
    await message.answer(text, reply_markup=payment_methods_kb(), parse_mode="Markdown")

async def portfolio_handler(message: types.Message):
    text = f"""📁 **أعمال {COMPANY_NAME}**
━━━━━━━━━━━━━━━━━━━━

🎨 **نماذج من مشاريعنا:**

🤖 **البوتات:**
• بوت متجر إلكتروني - 150$
• بوت حماية متقدم - 200$

📱 **التطبيقات:**
• تطبيق توصيل طلبات - 800$
• تطبيق إدارة مهام - 650$

💻 **المواقع:**
• موقع شركة - 350$
• موقع متجر - 550$

📌 **اختر نوع المشروع:**
"""
    await message.answer(text, reply_markup=portfolio_kb(), parse_mode="Markdown")

async def profile_handler(message: types.Message):
    user = await db.get_user(message.from_user.id)
    orders = await db.get_user_orders(message.from_user.id)
    
    points = user['loyalty_points'] if user else 0
    discount_percent = min(points // 10, 25)
    
    # حساب الإحصائيات
    total_orders = len(orders)
    pending_orders = len([o for o in orders if o['status'] == 'pending'])
    processing_orders = len([o for o in orders if o['status'] == 'processing'])
    completed_orders = len([o for o in orders if o['status'] == 'completed'])
    rejected_orders = len([o for o in orders if o['status'] == 'rejected'])
    
    text = f"""
👤 **معلومات حسابك - {COMPANY_NAME}**
━━━━━━━━━━━━━━━━━━━━

📊 **الإحصائيات:**
├ إجمالي الطلبات: {total_orders}
├ قيد المراجعة: {pending_orders} ⏳
├ قيد التنفيذ: {processing_orders} 🔄
├ مكتملة: {completed_orders} ✅
├ مرفوضة: {rejected_orders} ❌
└ نقاط الولاء: {points} 🪙

🎁 **مزاياك:**
├ خصم متاح: {discount_percent}%
└ الرصيد: {points * 0.1}$ (قابل للاستخدام)
📦 **طلباتك:**
"""
    
    if orders:
        for order in orders[:10]:
            status_info = {
                "pending": ("⏳", "قيد المراجعة", "yellow"),
                "processing": ("🔄", "قيد التنفيذ", "blue"),
                "completed": ("✅", "مكتمل", "green"),
                "rejected": ("❌", "مرفوض", "red")
            }.get(order['status'], ("⏳", "قيد المراجعة", "yellow"))
            
            emoji, status_text, _ = status_info
            
            date_str = "N/A"
            if hasattr(order.get('created_at'), 'strftime'):
                date_str = order['created_at'].strftime('%Y-%m-%d')
            elif order.get('created_at'):
                date_str = str(order['created_at'])[:10]
            
            text += f"""
┌────────────────
│ {emoji} **طلب #{order['id']}**
│ ├ الخدمة: {order['service_type']}
│ ├ الميزانية: {order['budget']}
│ ├ الحالة: {status_text}
│ └ التاريخ: {date_str}
└────────────────
"""
    else:
        text += "\n❌ **لا توجد طلبات بعد**\n🎁 ابدأ بطلبك الأول واحصل على خصم 10%!"
    
    text += f"""

💡 **كيف تربح نقاط؟**
• شارك البوت: +50 نقطة
• انضم للقناة: +30 نقطة
• كل طلب: +10 نقاط
• كل 10 نقاط = خصم 1$

👨‍💼 **المدير:** {ADMIN_USERNAME}
📢 **القناة:** {CHANNEL_LINK}
"""
    
    await message.answer(text, parse_mode="Markdown")

async def order_handler(message: types.Message, state: FSMContext):
    await state.set_state(OrderState.service_type)
        text = f"""
📝 **بدء طلب جديد - {COMPANY_NAME}**
━━━━━━━━━━━━━━━━━━━━

🎯 **اختر نوع الخدمة:**

💡 **نصيحة:** اختر الخدمة الأنسب لمشروعك
"""
    await message.answer(text, reply_markup=services_inline_kb(), parse_mode="Markdown")

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

📢 **تابعنا:** {CHANNEL_LINK}
"""
    await message.answer(text, reply_markup=support_kb(), parse_mode="Markdown")

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

⏱ **متوفر:** 9 صباحاً - 11 مساءً

🔗 **اضغط هنا:** https://t.me/{ADMIN_USERNAME.replace('@', '')}"""
    await message.answer(text, parse_mode="Markdown")

async def share_handler(message: types.Message):
    user = await db.get_user(message.from_user.id)
    points = user['loyalty_points'] if user else 0
    
    is_subscribed = await check_channel_subscription(message.from_user.id, message.bot)
    
    text = f"""
🤝 **شارك واربح - {COMPANY_NAME}**
━━━━━━━━━━━━━━━━━━━━

🎁 **برنامج الإحالة:**

💰 **كيف تربح؟**
1️⃣ شارك البوت مع أصدقائك: +50 نقطة
2️⃣ انضم للقناة: +30 نقطة
3️⃣ استبدل النقاط بخصومات!

🎯 **المكافآت:**
• 50 نقطة = خصم 5$
• 100 نقطة = خصم 10$
• 200 نقطة = خصم 25$ + هدية

📊 **رصيدك الحالي:** {points} نقطة
💵 **القيمة:** {points * 0.1}$

📤 **شارك الآن:**
اضغط الزر أدناه

📢 **القناة:** {CHANNEL_LINK}
{"✅ مشترك" if is_subscribed else "⚠️ غير مشترك"}
"""
    
    await message.answer(text, reply_markup=share_kb(), parse_mode="Markdown")

async def offers_handler(message: types.Message):
    text = f"""
🎁 **العروض والهدايا - {COMPANY_NAME}**
━━━━━━━━━━━━━━━━━━━━

🔥 **العروض الحالية:**

🎉 **عرض الطلب الأول:**
• خصم 10% على أول طلب
• الكود: FIRST10

🎊 **عرض الباقة الكاملة:**
• موقع + بوت + تطبيق• خصم 25%
• الكود: VEXO25

🏆 **برنامج الولاء:**
• اجمع نقاط مع كل طلب
• استبدلها بخصومات

🎟️ **كوبونات الخصم:**
• FIRST10 = 10% (الطلب الأول)
• VEXO15 = 15% (فوق 300$)
• SHARE20 = 20% (بعد المشاركة)
• VIP25 = 25% (فوق 1000$)

💡 **استخدم الكود عند الطلب!**
"""
    await message.answer(text, reply_markup=offers_kb(), parse_mode="Markdown")

# ==================== معالج Callback ====================

async def callback_handler(call: types.CallbackQuery, state: FSMContext):
    data = call.data
    
    # القائمة الرئيسية
    if data == "main_menu":
        await state.clear()
        await call.message.edit_text("📋 **القائمة الرئيسية:**", reply_markup=main_keyboard())
        await call.answer()
        return
    
    # اختيار الخدمة
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
            f"✅ **{service_name}**\n\n"
            f"📝 **أرسل تفاصيل المشروع:**\n"
            f"• ما الوظيفة المطلوبة؟\n"
            f"• ما الميزات الخاصة؟\n"            f"• هل هناك متطلبات إضافية؟\n\n"
            f"🔙 **للرجوع:** اضغط رجوع",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]
            ]),
            parse_mode="Markdown"
        )
        await call.answer()
        return
    
    # إدخال التفاصيل
    elif data == "main_menu" and await state.get_state() == OrderState.details:
        await state.clear()
        await call.message.edit_text("📋 **تم إلغاء الطلب**", reply_markup=main_keyboard())
        await call.answer()
        return
    
    # اختيار الميزانية
    elif data.startswith("budget_"):
        budget_map = {
            "budget_low": "أقل من 100$",
            "budget_mid": "100$ - 300$",
            "budget_high": "300$ - 1000$",
            "budget_premium": "أكثر من 1000$"
        }
        await state.update_data(budget=budget_map[data])
        
        data_state = await state.get_data()
        
        confirm_text = f"""
📋 **تأكيد الطلب - {COMPANY_NAME}**
━━━━━━━━━━━━━━━━━━━━

📦 **تفاصيل الطلب:**
├ الخدمة: {data_state.get('service_type')}
├ الميزانية: {budget_map[data]}
└ التفاصيل: {data_state.get('details')}

💡 **ملاحظات:**
• سيتم مراجعة طلبك خلال 24 ساعة
• بعد الموافقة، سيصلك إشعار
• يمكنك متابعة طلبك من 'حسابي'

✅ **اضغط 'تأكيد الطلب' للمتابعة**
"""
        
        await state.set_state(OrderState.confirm)
        await call.message.edit_text(
            confirm_text,
            reply_markup=confirmation_kb(),            parse_mode="Markdown"
        )
        await call.answer()
        return
    
    # تأكيد الطلب
    elif data == "order_confirm":
        data_state = await state.get_data()
        
        await db.add_user(
            user_id=call.from_user.id,
            username=call.from_user.username,
            full_name=call.from_user.full_name
        )
        
        order_id = await db.create_order(
            user_id=call.from_user.id,
            service_type=data_state.get("service_type", "عام"),
            details=data_state.get("details", ""),
            budget=data_state.get("budget", "غير محدد")
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
                f"├ الميزانية: {data_state.get('budget')}\n\n"
                f"🔔 **الحالة: قيد المراجعة**\n"
                f"💡 **تابع حسابك لمعرفة التحديثات**\n\n"
                f"👨‍💼 **المدير:** {ADMIN_USERNAME}",
                reply_markup=main_keyboard(),
                parse_mode="Markdown"
            )
            
            try:
                await call.message.bot.send_message(
                    config.ADMIN_ID,
                    f"🔔 **طلب جديد!**\n\n"
                    f"👤 المستخدم: {call.from_user.username or call.from_user.first_name}\n"
                    f"🆔 ID: {call.from_user.id}\n"
                    f"📦 الخدمة: {data_state.get('service_type')}\n"
                    f"💰 الميزانية: {data_state.get('budget')}\n"
                    f"📝 التفاصيل: {data_state.get('details')}"
                )            except:
                pass
        
        await call.answer()
        return
    
    # إلغاء الطلب
    elif data == "order_cancel":
        await state.clear()
        await call.message.edit_text(
            "❌ **تم إلغاء الطلب**\n\n"
            "يمكنك إنشاء طلب جديد في أي وقت!",
            reply_markup=main_keyboard(),
            parse_mode="Markdown"
        )
        await call.answer()
        return
    
    # طرق الدفع
    elif data.startswith("pay_"):
        payment_map = {
            "pay_jeew": "📱 جيب (Jeew)",
            "pay_jawali": "📲 جوالي (Jawali)",
            "pay_onecash": "💵 ون كاش (OneCash)",
            "pay_monee": "💰 موني (Monee)",
            "pay_floosak": "💳 فلوسك (Floosak)",
            "pay_kareemi": "💰 الكريمي",
            "pay_tadhamon": "🤝 تضامن",
            "pay_yemen_kuwait": "🏛 بنك اليمن والكويت"
        }
        payment_name = payment_map.get(data, "طريقة الدفع")
        
        await call.message.edit_text(
            f"✅ {payment_name}\n\n"
            f"📝 **سيتم إرسال تفاصيل الدفع**\n"
            f"بعد تأكيد طلبك\n\n"
            f"💡 **لبدء الطلب:** اضغط 'طلب جديد'",
            reply_markup=payment_methods_kb()
        )
        await call.answer()
        return
    
    # المشاركة
    elif data == "share_claim":
        user = await db.get_user(call.from_user.id)
        points = user['loyalty_points'] if user else 0
        
        is_subscribed = await check_channel_subscription(call.from_user.id, call.message.bot)
        
        # إضافة نقاط إذا انضم للقناة        points_added = False
        if is_subscribed:
            # تحقق إذا لم يحصل على النقاط من قبل
            user_data = await db.get_user(call.from_user.id)
            if user_data and not user_data.get('joined_channel_points', False):
                await add_join_points(call.from_user.id)
                await db.execute_query(
                    "UPDATE users SET joined_channel_points = TRUE WHERE id = $1",
                    call.from_user.id
                )
                points_added = True
        
        new_points = points + (30 if points_added else 0)
        
        await call.message.edit_text(
            f"🎁 **رصيدك من النقاط:** {new_points}\n\n"
            f"💰 **القيمة:** {new_points * 0.1}$\n"
            f"{'✅ حصلت على 30 نقطة للانضمام للقناة!' if points_added else ''}\n\n"
            f"📤 **شارك الآن واربح 50 نقطة!**\n"
            f"🔗 رابط البوت: @VexoServiceBot\n\n"
            f"📢 **القناة:** {CHANNEL_LINK}",
            reply_markup=share_kb()
        )
        await call.answer()
        return
    
    # الأعمال (Portfolio)
    elif data.startswith("port_"):
        project_type_map = {
            "port_bot": "bot",
            "port_app": "app",
            "port_web": "web",
            "port_store": "store"
        }
        
        p_type = project_type_map.get(data)
        if p_type:
            projects = await db.get_portfolio(p_type)
        else:
            projects = await db.get_portfolio()
        
        if projects:
            text = "📁 **المشاريع:**\n\n"
            for proj in projects[:5]:
                text += f"┌────────────────\n"
                text += f"│ **{proj['title']}**\n"
                if proj.get('price'):
                    text += f"│ 💰 السعر: {proj['price']}\n"
                if proj.get('description'):
                    desc = proj['description'][:150]                    text += f"│ 📝 {desc}{'...' if len(proj['description']) > 150 else ''}\n"
                if proj.get('features'):
                    text += f"│ ⭐ الميزات: {proj['features']}\n"
                if proj.get('preview_link'):
                    text += f"│ 🔗 [معاينة]({proj['preview_link']})\n"
                text += f"└────────────────\n\n"
            
            await call.message.edit_text(text, reply_markup=portfolio_kb(), parse_mode="Markdown")
        else:
            await call.message.edit_text("📌 **قريباً...**", reply_markup=portfolio_kb())
        
        await call.answer()
        return
    
    # الدعم الفني
    elif data == "ticket_new":
        await state.set_state(SupportState.message)
        await call.message.edit_text(
            "🎫 **فتح تذكرة دعم جديدة**\n\n"
            "📝 **اكتب مشكلتك بالتفصيل:**",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 إلغاء", callback_data="main_menu")]
            ])
        )
        await call.answer()
        return
    
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
        await call.answer()
        return
    
    elif data == "faq":
        faq_text = f"""
❓ **الأسئلة الشائعة - {COMPANY_NAME}**
━━━━━━━━━━━━━━━━━━━━

**س: كم وقت التنفيذ؟**
ج: 3-7 أيام للبوتات، 7-14 يوم للتطبيقات

**س: هل هناك ضمان؟**
ج: نعم، ضمان 30 يوم على جميع المشاريع
**س: طرق الدفع؟**
ج: محافظ محلية (جيب، ون كاش...) وبنوك يمنية

**س: هل هناك دعم بعد التسليم؟**
ج: نعم، دعم مجاني لمدة شهر

**س: كيف أربح نقاط؟**
ج: شارك البوت (+50)، انضم للقناة (+30)، اطلب (+10)

👨‍💼 **للاستفسار:** {ADMIN_USERNAME}
📢 **القناة:** {CHANNEL_LINK}
"""
        await call.message.edit_text(faq_text, reply_markup=support_kb(), parse_mode="Markdown")
        await call.answer()
        return
    
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
        await call.answer()
        return
    
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
        await call.answer()
        return
    
    elif data == "offers_loyalty":
        await call.message.edit_text(
            "🏆 **برنامج الولاء**\n\n"
            "💰 **كيف يعمل؟**\n"
            "• كل طلب = 10 نقطة\n"
            "• مشاركة البوت = 50 نقطة\n"
            "• الانضمام للقناة = 30 نقطة\n"            "• كل 10 نقاط = 1$ خصم\n\n"
            "🎁 **مستويات الولاء:**\n"
            "🥉 برونزي: 0-100 نقطة\n"
            "🥈 فضي: 100-500 نقطة\n"
            "🥇 ذهبي: 500+ نقطة\n\n"
            "💎 **مزايا الذهب:** خصم إضافي 5%",
            reply_markup=offers_kb()
        )
        await call.answer()
        return
    
    await call.answer()

# ==================== معالج الرسائل النصية ====================

async def handle_text(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state == OrderState.details:
        await state.update_data(details=message.text)
        await state.set_state(OrderState.budget)
        await message.answer(
            "💰 **اختر الميزانية المتوقعة:**\n\n"
            "💡 **نصيحة:** اختر الميزانية الأقرب لمشروعك",
            reply_markup=budget_kb(),
            parse_mode="Markdown"
        )
        return
    
    elif current_state == SupportState.message:
        ticket_id = await db.create_ticket(message.from_user.id, message.text)
        await state.clear()
        
        await message.answer(
            f"✅ **تم فتح تذكرة الدعم!**\n\n"
            f"🎫 رقم التذكرة: #{ticket_id}\n"
            f"📝 رسالتك: {message.text[:100]}...\n\n"
            f"⏱ **سنرد عليك خلال 24 ساعة**\n"
            f"💬 **للتواصل السريع:** {SUPPORT_USERNAME}",
            reply_markup=main_keyboard(),
            parse_mode="Markdown"
        )
        
        try:
            await message.bot.send_message(
                config.ADMIN_ID,
                f"🎫 **تذكرة دعم جديدة!**\n\n"
                f"👤 المستخدم: {message.from_user.username or message.from_user.first_name}\n"
                f"🆔 ID: {message.from_user.id}\n"
                f"🎫 الرقم: #{ticket_id}\n"                f"📝 الرسالة: {message.text}"
            )
        except:
            pass
        return

# ==================== تسجيل المعالجات ====================

def register_handlers(dp: Dispatcher):
    dp.message.register(start_handler, Command("start"))
    dp.message.register(services_handler, F.text == "🎯 خدماتنا")
    dp.message.register(portfolio_handler, F.text == "📁 أعمالنا")
    dp.message.register(profile_handler, F.text == "👤 حسابي")
    dp.message.register(order_handler, F.text == "📝 طلب جديد")
    dp.message.register(support_handler, F.text == "💬 الدعم الفني")
    dp.message.register(contact_admin, F.text == "📞 الإدارة")
    dp.message.register(share_handler, F.text == "🤝 شارك واربح")
    dp.message.register(offers_handler, F.text == "🎁 العروض والهدايا")
    dp.message.register(payment_handler, F.text == "💳 طرق الدفع")
    
    dp.message.register(handle_text)
    dp.callback_query.register(callback_handler)
