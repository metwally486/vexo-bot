from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import config
import database as db
import random
from datetime import datetime, timedelta

# ==================== حالات النموذج ====================

class OrderState(StatesGroup):
    service_type = State()
    service_category = State()
    details = State()
    budget = State()
    payment_method = State()
    confirm = State()

class SupportState(StatesGroup):
    message = State()

class PaymentState(StatesGroup):
    amount = State()
    wallet = State()

# ==================== الأزرار الرئيسية ====================

def main_keyboard():
    kb = [
        [KeyboardButton(text="🎯 خدماتنا"), KeyboardButton(text="📝 طلب جديد")],
        [KeyboardButton(text="🎁 العروض والهدايا"), KeyboardButton(text="💳 طرق الدفع")],
        [KeyboardButton(text="📁 أعمالنا"), KeyboardButton(text="👤 حسابي")],
        [KeyboardButton(text="🤝 شارك واربح"), KeyboardButton(text="💬 الدعم الفني")],
        [KeyboardButton(text="📞 تواصل مع المدير")]
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

def payment_methods_kb():
    kb = [
        [InlineKeyboardButton(text="📱 جيب (Jeew)", callback_data="pay_jeew")],
        [InlineKeyboardButton(text="💳 ون كاش (OneCash)", callback_data="pay_onecash")],
        [InlineKeyboardButton(text="💰 كريمي (Kareemi)", callback_data="pay_kareemi")],
        [InlineKeyboardButton(text="📲 جوالي (Jawali)", callback_data="pay_jawali")],
        [InlineKeyboardButton(text="💵 موني (Monee)", callback_data="pay_monee")],
        [InlineKeyboardButton(text="🌍 تحويل دولي (532174)", callback_data="pay_international")],
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
        [InlineKeyboardButton(text="👨‍💻 الدعم الفني المباشر", url="https://t.me/m_7_1_1_w")],
        [InlineKeyboardButton(text="📞 المدير", url="https://t.me/abohamed12")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def portfolio_kb():
    kb = [
        [InlineKeyboardButton(text="🤖 البوتات", callback_data="port_bot")],
        [InlineKeyboardButton(text="📱 التطبيقات", callback_data="port_app")],
        [InlineKeyboardButton(text="💻 المواقع", callback_data="port_web")],
        [InlineKeyboardButton(text="🛒 المتاجر", callback_data="port_store")],
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def share_kb():
    kb = [
        [InlineKeyboardButton(text="📤 مشاركة البوت", switch_inline_query="🎉 انضم لي على Vexo Bot للخدمات التقنية! ")],
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

# ==================== المعالجات ====================

async def start_handler(message: types.Message):
    await db.add_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    
    welcome_text = f"""
🌟 **أهلاً وسهلاً بك في Vexo Bot** 🌟
━━━━━━━━━━━━━━━━━━━━

👋 **مرحباً:** {message.from_user.first_name}
🤖 **بوت الخدمات التقنية المتكامل**

💎 **لماذا تختارنا؟**
✅ أسعار منافسة وجودة عالية
✅ تسليم سريع وضمان حقيقي
✅ دعم فني 24/7
✅ طرق دفع متعددة ومرنة

🎁 **عروض خاصة:**
🔸 خصم 10% للطلب الأول
🔸 خصم 15% عند مشاركة البوت
🔸 نقاط ولاء على كل طلب

📌 **اختر من القائمة:**
"""
    
    await message.answer(
        welcome_text,
        reply_markup=main_keyboard(),
        parse_mode="Markdown"
    )
    
    await message.answer(
        "🎉 **استخدم /help لمعرفة جميع الأوامر**",
        parse_mode="Markdown"
    )

async def services_handler(message: types.Message):
    text = """
🎯 **خدماتنا التقنية المتكاملة**
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
"""
    await message.answer(text, reply_markup=services_inline_kb(), parse_mode="Markdown")

async def payment_handler(message: types.Message):
    text = """💳 **طرق الدفع المتاحة**
━━━━━━━━━━━━━━━━━━━━

📱 **المحافظ المحلية:**

1️⃣ **جيب (Jeew)**
   📲 الرقم: يُرسل بعد تأكيد الطلب
   ⏱ التفعيل: فوري

2️⃣ **ون كاش (OneCash)**
   📲 الرقم: يُرسل بعد تأكيد الطلب
   ⏱ التفعيل: فوري

3️⃣ **كريمي (Kareemi)**
   📲 الرقم: يُرسل بعد تأكيد الطلب
   ⏱ التفعيل: خلال ساعة

4️⃣ **جوالي (Jawali)**
   📲 الرقم: يُرسل بعد تأكيد الطلب
   ⏱ التفعيل: فوري

5️⃣ **موني (Monee)**
   📲 الرقم: يُرسل بعد تأكيد الطلب
   ⏱ التفعيل: فوري

🌍 **التحويل الدولي:**
   🏦 رقم الحساب: 532174
   💵 حدد المبلغ عند الطلب
   ⏱ التفعيل: 24-48 ساعة

📝 **ملاحظات مهمة:**
• يتم إرسال تفاصيل الدفع بعد تأكيد الطلب
• يحتفظ بالإيصال بعد التحويل
• يتم تفعيل الطلب خلال 24 ساعة
• الحد الأدنى للطلب: 50$

💡 **لبدء الطلب:** اضغط 'طلب جديد'
"""
    await message.answer(text, reply_markup=payment_methods_kb(), parse_mode="Markdown")

async def portfolio_handler(message: types.Message):
    text = """
📁 **أعمالنا ومشاريعنا**
━━━━━━━━━━━━━━━━━━━━

🎨 **نماذج من أعمالنا:**

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
    await message.answer(text, reply_markup=portfolio_kb(), parse_mode="Markdown")

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
"""
    
    await message.answer(text, parse_mode="Markdown")

async def order_handler(message: types.Message, state: FSMContext):
    await state.set_state(OrderState.service_type)
    
    text = """
📝 **بدء طلب جديد**
━━━━━━━━━━━━━━━━━━━━

🎯 **اختر نوع الخدمة:**

💡 **نصيحة:** اختر الخدمة الأنسب لمشروعك
"""
    await message.answer(text, reply_markup=services_inline_kb(), parse_mode="Markdown")

async def support_handler(message: types.Message):
    text = """
💬 **الدعم الفني**
━━━━━━━━━━━━━━━━━━━━
👨‍ **فريقنا جاهز لمساعدتك!**

📞 **التواصل المباشر:**
├ المدير: @abohamed12
└ الدعم الفني: @m_7_1_1_w

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
"""
    await message.answer(text, reply_markup=support_kb(), parse_mode="Markdown")

async def contact_admin(message: types.Message):
    text = f"""
📞 **تواصل مع المدير**
━━━━━━━━━━━━━━━━━━━━

👤 **المدير:** @abohamed12

💡 **متى تتواصل؟**
• للاستفسارات المهمة
• للمشاريع الكبيرة
• للشكاوى والاقتراحات

⏱ **متوفر:** 9 صباحاً - 11 مساءً

🔗 **اضغط هنا للتواصل:**
https://t.me/abohamed12
"""
    await message.answer(text, parse_mode="Markdown")

async def share_handler(message: types.Message):
    user = await db.get_user(message.from_user.id)
    points = user['loyalty_points'] if user else 0
    
    text = f"""
🤝 **شارك واربح**
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
"""
    await message.answer(text, reply_markup=share_kb(), parse_mode="Markdown")

async def offers_handler(message: types.Message):
    text = """
🎁 **العروض والهدايا**
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

💡 **استخدم الكود عند الطلب!**"""
    await message.answer(text, reply_markup=offers_kb(), parse_mode="Markdown")

async def callback_handler(call: types.CallbackQuery, state: FSMContext):
    data = call.data
    
    if data == "main_menu":
        await call.message.edit_text("📋 **القائمة الرئيسية:**", reply_markup=main_keyboard())
    
    elif data == "srv_create_bot":
        await state.update_data(service_type="🤖 إنشاء بوت تلجرام")
        await state.set_state(OrderState.details)
        await call.message.edit_text(
            "✅ **إنشاء بوت تلجرام**\n\n"
            "📝 **أرسل تفاصيل البوت المطلوب:**\n"
            "• ما وظيفة البوت؟\n"
            "• ما الميزات المطلوبة؟\n"
            "• هل هناك متطلبات خاصة?",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]])
        )
    
    elif data == "srv_dev_bot":
        await state.update_data(service_type="⚙️ تطوير بوت موجود")
        await state.set_state(OrderState.details)
        await call.message.edit_text(
            "✅ **تطوير بوت موجود**\n\n"
            "📝 **أرسل:**\n"
            "• رابط البوت الحالي\n"
            "• التطويرات المطلوبة\n"
            "• المشاكل الحالية",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]])
        )
    
    elif data == "srv_android":
        await state.update_data(service_type="📱 تطبيق أندرويد")
        await state.set_state(OrderState.details)
        await call.message.edit_text(
            "✅ **تطبيق أندرويد**\n\n"
            "📝 **أرسل تفاصيل التطبيق:**\n"
            "• نوع التطبيق (متجر، خدمة، لعبة...)\n"
            "• الميزات المطلوبة\n"
            "• التصميم المطلوب",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]])
        )
    
    elif data == "srv_ios":
        await state.update_data(service_type="🍎 تطبيق iOS")
        await state.set_state(OrderState.details)
        await call.message.edit_text(
            "✅ **تطبيق iOS**\n\n"
            "📝 **أرسل تفاصيل التطبيق:**",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]])
        )
    
    elif data == "srv_website":
        await state.update_data(service_type="💻 موقع إلكتروني")
        await state.set_state(OrderState.details)
        await call.message.edit_text(
            "✅ **موقع إلكتروني**\n\n"
            "📝 **أرسل:**\n"
            "• نوع الموقع\n"
            "• الصفحات المطلوبة\n"
            "• الميزات الخاصة",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]])
        )
    
    elif data == "srv_store":
        await state.update_data(service_type="🛒 متجر إلكتروني")
        await state.set_state(OrderState.details)
        await call.message.edit_text(
            "✅ **متجر إلكتروني**\n\n"
            "📝 **أرسل:**\n"
            "• نوع المنتجات\n"
            "• طرق الدفع المطلوبة\n"
            "• الميزات الإضافية",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]])
        )
    
    elif data == "srv_scripts":
        await state.update_data(service_type="🔧 معاملات برمجية")
        await state.set_state(OrderState.details)
        await call.message.edit_text(
            "✅ **معاملات برمجية**\n\n"
            "📝 **أرسل:**\n"
            "• نوع السكريبت\n"
            "• الوظيفة المطلوبة\n"
            "• اللغة المفضلة",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 رجوع", callback_data="main_menu")]])
        )
    
    elif data == "srv_premium":
        await call.message.edit_text(
            "🎁 **الخدمات المميزة**\n\n"
            "💎 **باقات VIP:**\n\n"
            "🥇 **الباقة الذهبية** (1000$):\n"
            "• بوت + موقع + تطبيق\n"
            "• دعم لمدة سنة\n"
            "• تحديثات مجانية\n\n"
            "🥈 **الباقة الفضية** (500$):\n"
            "• بوت + موقع\n"
            "• دعم 6 أشهر\n\n"
            "📞 **للاستفسار:** @abohamed12",
            reply_markup=services_inline_kb()
        )
    
    elif data.startswith("budget_"):
        budget_map = {
            "budget_low": "أقل من 100$",
            "budget_mid": "100$ - 300$",
            "budget_high": "300$ - 1000$",
            "budget_premium": "أكثر من 1000$"
        }
        await state.update_data(budget=budget_map[data])
        
        data_state = await state.get_data()
        await db.create_order(
            user_id=call.from_user.id,
            service_type=data_state.get("service_type", "عام"),
            details=data_state.get("details", ""),
            budget=budget_map[data]
        )
        
        await db.add_points(call.from_user.id, 10)
        await state.clear()
        
        await call.message.edit_text(
            f"✅ **تم استلام طلبك بنجاح!**\n\n"
            f"🎉 **تهانينا!** حصلت على 10 نقاط ولاء\n\n"
            f"📦 **تفاصيل الطلب:**\n"
            f"├ الخدمة: {data_state.get('service_type')}\n"
            f"├ الميزانية: {budget_map[data]}\n"
            f"└ التفاصيل: {data_state.get('details')[:100]}...\n\n"
            f"🔔 **سيتم مراجعته خلال 24 ساعة**\n"
            f"💡 **تابع حسابك لمعرفة التحديثات**",
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
        await call.message.edit_text("📋 **تذاكرك السابقة:**\n\n⏳ قريباً...", reply_markup=support_kb())
    
    elif data == "faq":
        faq_text = """
❓ **الأسئلة الشائعة**
━━━━━━━━━━━━━━━━━━━━

**س: كم وقت التنفيذ؟**
ج: 3-7 أيام للبوتات، 7-14 يوم للتطبيقات

**س: هل هناك ضمان؟**
ج: نعم، ضمان 30 يوم على جميع المشاريع

**س: طرق الدفع؟**
ج: محافظ محلية (جيب، ون كاش...) وتحويل دولي

**س: هل هناك دعم بعد التسليم؟**
ج: نعم، دعم مجاني لمدة شهر

**س: كيف أطلب؟**
ج: اضغط 'طلب جديد' واتبع الخطوات

**س: هل يمكن التعديل بعد التسليم؟**
ج: نعم، بسعر مناسب حسب التعديل

**س: كيف أربح نقاط؟**
ج: اطلب، شارك البوت، احصل على مكافآت
"""
        await call.message.edit_text(faq_text, reply_markup=support_kb())
    
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
            f"🔗 رابط البوت: @VexoServiceBot",
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
    
    elif data.startswith("port_"):
        await call.message.edit_text("📌 **قريباً...**\n\nنعمل على إضافة الأعمال!", reply_markup=portfolio_kb())
    
    elif data.startswith("pay_"):
        await call.message.edit_text(
            "💳 **طرق الدفع**\n\n"
            "📝 **سيتم إرسال تفاصيل الدفع**\n"
            "بعد تأكيد طلبك\n\n"
            "💡 **لبدء الطلب:** اضغط 'طلب جديد'",
            reply_markup=payment_methods_kb()
        )
    
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
            f"💬 **للتواصل السريع:** @m_7_1_1_w",
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
    dp.message.register(contact_admin, F.text == "📞 تواصل مع المدير")
    dp.message.register(share_handler, F.text == "🤝 شارك واربح")
    dp.message.register(offers_handler, F.text == "🎁 العروض والهدايا")
    
    dp.message.register(handle_order_details, ~F.text.in_([
        "🎯 خدماتنا", "📁 أعمالنا", "👤 حسابي", "📝 طلب جديد",
        "💬 الدعم الفني", "💳 طرق الدفع", "📞 تواصل مع المدير",
        "🤝 شارك واربح", "🎁 العروض والهدايا"
    ]))
    
    dp.callback_query.register(callback_handler)
