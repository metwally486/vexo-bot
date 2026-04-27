"""
bot.py — Vexo Bot Handlers (aiogram 3.x)
يتضمن: أوامر المستخدم + لوحة الأدمن + نقاط الولاء + تذاكر الدعم + معرض الأعمال
"""
import asyncio
import config
import database as db
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

router = Router()

# ══════════════════════════════════════════════════════════════
# الحالات (FSM States)
# ══════════════════════════════════════════════════════════════

class OrderState(StatesGroup):
    service   = State()
    details   = State()
    budget    = State()
    confirm   = State()

class TicketState(StatesGroup):
    subject   = State()
    message   = State()
    confirm   = State()

class AdminState(StatesGroup):
    broadcast      = State()
    reply_ticket   = State()
    add_portfolio  = State()
    order_notes    = State()


# ══════════════════════════════════════════════════════════════
# لوحات المفاتيح المشتركة
# ══════════════════════════════════════════════════════════════

def main_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="📦 طلب خدمة"), KeyboardButton(text="🖼️ معرض أعمالنا")],
        [KeyboardButton(text="🎫 الدعم الفني"), KeyboardButton(text="💎 نقاطي")],
        [KeyboardButton(text="📋 طلباتي"),     KeyboardButton(text="ℹ️ من نحن")],
    ]
    if is_admin:
        buttons.append([KeyboardButton(text="🔐 لوحة الأدمن")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ إلغاء")]],
        resize_keyboard=True,
    )

def budget_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💵 أقل من 100$"), KeyboardButton(text="💵 100$ - 300$")],
            [KeyboardButton(text="💵 300$ - 1000$"), KeyboardButton(text="💵 أكثر من 1000$")],
            [KeyboardButton(text="❌ إلغاء")],
        ],
        resize_keyboard=True,
    )

def services_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🤖 بوت تلجرام"), KeyboardButton(text="💻 موقع إلكتروني")],
            [KeyboardButton(text="📱 تطبيق جوال"), KeyboardButton(text="🎨 تصميم جرافيك")],
            [KeyboardButton(text="📊 لوحة تحكم"), KeyboardButton(text="🔧 خدمة أخرى")],
            [KeyboardButton(text="❌ إلغاء")],
        ],
        resize_keyboard=True,
    )

def admin_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 الطلبات المعلقة"), KeyboardButton(text="🎫 التذاكر المفتوحة")],
            [KeyboardButton(text="👥 المستخدمين"),       KeyboardButton(text="📊 الإحصائيات")],
            [KeyboardButton(text="📢 بث رسالة"),         KeyboardButton(text="🖼️ إدارة المعرض")],
            [KeyboardButton(text="🏠 الرئيسية")],
        ],
        resize_keyboard=True,
    )

def order_actions_inline(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ قبول",    callback_data=f"order_accept_{order_id}"),
            InlineKeyboardButton(text="⚙️ تنفيذ",   callback_data=f"order_processing_{order_id}"),
        ],
        [
            InlineKeyboardButton(text="❌ رفض",     callback_data=f"order_reject_{order_id}"),
            InlineKeyboardButton(text="📝 ملاحظة",  callback_data=f"order_note_{order_id}"),
        ],
    ])

def ticket_actions_inline(ticket_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💬 رد",      callback_data=f"ticket_reply_{ticket_id}"),
            InlineKeyboardButton(text="✅ إغلاق",   callback_data=f"ticket_close_{ticket_id}"),
        ],
    ])

def confirm_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ تأكيد"), KeyboardButton(text="❌ إلغاء")],
        ],
        resize_keyboard=True,
    )


# ══════════════════════════════════════════════════════════════
# مساعدات داخلية
# ══════════════════════════════════════════════════════════════

def is_admin(user_id: int) -> bool:
    return user_id == config.ADMIN_ID


async def ensure_user(message: Message) -> dict | None:
    """تسجيل / تحديث المستخدم في قاعدة البيانات"""
    u = message.from_user
    await db.upsert_user(u.id, u.username, u.full_name)
    return await db.get_user(u.id)


async def notify_admin(bot: Bot, text: str, reply_markup=None):
    """إرسال إشعار للأدمن"""
    try:
        await bot.send_message(config.ADMIN_ID, text, reply_markup=reply_markup, parse_mode="HTML")
    except Exception as e:
        print(f"⚠️ notify_admin error: {e}")


# ══════════════════════════════════════════════════════════════
# /start  و الرئيسية
# ══════════════════════════════════════════════════════════════

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    user = await ensure_user(message)
    admin = is_admin(message.from_user.id)

    welcome = (
        f"👋 أهلاً <b>{message.from_user.first_name}</b>!\n\n"
        "🚀 مرحباً بك في <b>Vexo للخدمات التقنية</b>\n"
        "نقدم لك أفضل الحلول التقنية بأسعار تنافسية.\n\n"
        "🎯 اختر من القائمة أدناه:"
    )

    # نقاط الترحيب للمستخدمين الجدد
    if user and user.get("loyalty_points", 0) == 0:
        await db.add_points(message.from_user.id, 10, "welcome_bonus")
        welcome += "\n\n🎁 <b>حصلت على 10 نقاط ترحيبية!</b>"

    await message.answer(
        welcome,
        reply_markup=main_keyboard(admin),
        parse_mode="HTML",
    )


@router.message(F.text == "🏠 الرئيسية")
async def go_home(message: Message, state: FSMContext):
    await state.clear()
    admin = is_admin(message.from_user.id)
    await message.answer(
        "🏠 القائمة الرئيسية:", reply_markup=main_keyboard(admin)
    )


@router.message(F.text == "❌ إلغاء")
async def cancel_action(message: Message, state: FSMContext):
    await state.clear()
    admin = is_admin(message.from_user.id)
    await message.answer("✅ تم الإلغاء.", reply_markup=main_keyboard(admin))


# ══════════════════════════════════════════════════════════════
# من نحن
# ══════════════════════════════════════════════════════════════

@router.message(F.text == "ℹ️ من نحن")
async def about_us(message: Message):
    text = (
        "🏢 <b>Vexo للخدمات التقنية</b>\n\n"
        "نحن فريق متخصص في تطوير الحلول التقنية المتكاملة:\n\n"
        "🤖 <b>بوتات تلجرام</b> — متجر، حجز، دعم، تداول\n"
        "💻 <b>مواقع إلكترونية</b> — احترافية وسريعة\n"
        "📱 <b>تطبيقات جوال</b> — iOS & Android\n"
        "🎨 <b>تصميم جرافيك</b> — هوية بصرية متكاملة\n"
        "📊 <b>لوحات تحكم</b> — إدارة سهلة وذكية\n\n"
        "⭐ <b>ضمان الجودة وسرعة التسليم</b>\n"
        "💬 الدعم الفني متاح 24/7"
    )
    await message.answer(text, parse_mode="HTML")


# ══════════════════════════════════════════════════════════════
# معرض الأعمال
# ══════════════════════════════════════════════════════════════

@router.message(F.text == "🖼️ معرض أعمالنا")
async def show_portfolio(message: Message):
    items = await db.get_portfolio(limit=10)
    if not items:
        await message.answer("📂 لا توجد مشاريع في المعرض حالياً.")
        return

    await message.answer("🖼️ <b>أبرز أعمالنا:</b>", parse_mode="HTML")
    for item in items:
        text = (
            f"<b>{item['title']}</b>\n"
            f"📂 النوع: {item['type']}\n"
        )
        if item.get("description"):
            text += f"📝 {item['description']}\n"
        if item.get("price"):
            text += f"💰 السعر يبدأ من: {item['price']}\n"

        buttons = []
        if item.get("preview_link"):
            buttons.append([InlineKeyboardButton(text="🔗 معاينة", url=item["preview_link"])])

        markup = InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None

        if item.get("image_url"):
            try:
                await message.answer_photo(
                    item["image_url"], caption=text,
                    parse_mode="HTML", reply_markup=markup
                )
            except Exception:
                await message.answer(text, parse_mode="HTML", reply_markup=markup)
        else:
            await message.answer(text, parse_mode="HTML", reply_markup=markup)


# ══════════════════════════════════════════════════════════════
# نقاط الولاء
# ══════════════════════════════════════════════════════════════

@router.message(F.text == "💎 نقاطي")
async def show_points(message: Message, bot: Bot):
    user = await ensure_user(message)
    if not user:
        await message.answer("❌ حدث خطأ، حاول مجدداً.")
        return

    points = user.get("loyalty_points", 0)
    channel_bonus = user.get("joined_channel_points", False)

    text = (
        f"💎 <b>نقاطك:</b> {points} نقطة\n"
        f"💵 <b>القيمة:</b> {points // config.POINTS_REDEEM_RATE:.1f}$\n\n"
    )

    markup = None
    if not channel_bonus and config.CHANNEL_USERNAME:
        text += (
            f"🎁 <b>احصل على {config.POINTS_ON_JOIN_CHANNEL} نقطة إضافية</b>\n"
            f"بمجرد الاشتراك في قناتنا!"
        )
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 اشترك في القناة", url=f"https://t.me/{config.CHANNEL_USERNAME.lstrip('@')}")],
            [InlineKeyboardButton(text="✅ تحقق من اشتراكي", callback_data="check_channel_join")],
        ])
    else:
        text += (
            "🎯 كيف تكسب نقاطاً:\n"
            f"• طلب خدمة → +{config.POINTS_ON_ORDER} نقاط\n"
            f"• الانضمام للقناة → +{config.POINTS_ON_JOIN_CHANNEL} نقاط\n"
            "• مشاركة أصدقاء → نقاط إضافية قريباً\n\n"
            f"💡 كل {config.POINTS_REDEEM_RATE} نقطة = 1$ خصم على طلباتك"
        )

    await message.answer(text, parse_mode="HTML", reply_markup=markup)


@router.callback_query(F.data == "check_channel_join")
async def check_channel_join(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    already = await db.get_user_channel_status(user_id)
    if already:
        await callback.answer("✅ لقد حصلت على النقاط مسبقاً!", show_alert=True)
        return

    try:
        member = await bot.get_chat_member(config.CHANNEL_ID, user_id)
        if member.status in ("member", "administrator", "creator"):
            await db.mark_channel_joined(user_id)
            await db.add_points(user_id, config.POINTS_ON_JOIN_CHANNEL, "channel_join")
            await callback.answer(
                f"🎉 تم! حصلت على {config.POINTS_ON_JOIN_CHANNEL} نقطة!", show_alert=True
            )
            await callback.message.edit_reply_markup()
        else:
            await callback.answer(
                "❌ لم يتم الاشتراك بعد. اشترك ثم اضغط تحقق.", show_alert=True
            )
    except Exception:
        await callback.answer("❌ تعذر التحقق، تأكد من الاشتراك وأعد المحاولة.", show_alert=True)


# ══════════════════════════════════════════════════════════════
# طلب خدمة (FSM)
# ══════════════════════════════════════════════════════════════

@router.message(F.text == "📦 طلب خدمة")
async def order_start(message: Message, state: FSMContext):
    user = await ensure_user(message)
    if not user:
        await message.answer("❌ حدث خطأ، حاول مجدداً.")
        return
    if user.get("is_blocked"):
        await message.answer("🚫 حسابك محظور. تواصل مع الدعم.")
        return

    # فحص حد الطلبات اليومية
    count_today = await db.count_user_orders_today(message.from_user.id)
    if count_today >= config.MAX_ORDERS_PER_DAY:
        await message.answer(
            f"⚠️ وصلت للحد الأقصى ({config.MAX_ORDERS_PER_DAY} طلبات يومياً).\n"
            "حاول غداً أو تواصل مع الدعم."
        )
        return

    await state.set_state(OrderState.service)
    await message.answer(
        "🛒 <b>طلب خدمة جديدة</b>\n\nاختر نوع الخدمة:",
        parse_mode="HTML",
        reply_markup=services_keyboard(),
    )


@router.message(OrderState.service)
async def order_service(message: Message, state: FSMContext):
    if message.text == "❌ إلغاء":
        await state.clear()
        await go_home(message, state)
        return
    await state.update_data(service=message.text)
    await state.set_state(OrderState.details)
    await message.answer(
        f"✅ الخدمة: <b>{message.text}</b>\n\n"
        "📝 اشرح تفاصيل طلبك بدقة (ميزات، متطلبات، تفضيلات):",
        parse_mode="HTML",
        reply_markup=cancel_keyboard(),
    )


@router.message(OrderState.details)
async def order_details(message: Message, state: FSMContext):
    if message.text == "❌ إلغاء":
        await state.clear()
        await go_home(message, state)
        return
    if len(message.text) < 20:
        await message.answer("⚠️ الرجاء كتابة وصف أكثر تفصيلاً (20 حرف على الأقل).")
        return
    await state.update_data(details=message.text)
    await state.set_state(OrderState.budget)
    await message.answer(
        "💰 ما هي ميزانيتك التقريبية؟",
        reply_markup=budget_keyboard(),
    )


@router.message(OrderState.budget)
async def order_budget(message: Message, state: FSMContext):
    if message.text == "❌ إلغاء":
        await state.clear()
        await go_home(message, state)
        return
    await state.update_data(budget=message.text)
    data = await state.get_data()
    await state.set_state(OrderState.confirm)
    summary = (
        "📋 <b>ملخص طلبك:</b>\n\n"
        f"🔧 <b>الخدمة:</b> {data['service']}\n"
        f"📝 <b>التفاصيل:</b>\n{data['details']}\n\n"
        f"💰 <b>الميزانية:</b> {data['budget']}\n\n"
        "هل تريد تأكيد الطلب؟"
    )
    await message.answer(summary, parse_mode="HTML", reply_markup=confirm_keyboard())


@router.message(OrderState.confirm)
async def order_confirm(message: Message, state: FSMContext, bot: Bot):
    if message.text == "❌ إلغاء":
        await state.clear()
        await go_home(message, state)
        return
    if message.text != "✅ تأكيد":
        await message.answer("⚠️ اضغط تأكيد أو إلغاء.")
        return

    data = await state.get_data()
    user_id = message.from_user.id
    order_id = await db.create_order(
        user_id, data["service"], data["details"], data["budget"]
    )
    await state.clear()

    if not order_id:
        await message.answer("❌ فشل إنشاء الطلب، حاول مجدداً.")
        return

    await db.add_points(user_id, config.POINTS_ON_ORDER, f"order_{order_id}")
    admin = is_admin(user_id)
    await message.answer(
        f"✅ <b>تم إرسال طلبك!</b>\n"
        f"🔢 رقم الطلب: <code>#{order_id}</code>\n"
        f"🎁 كسبت {config.POINTS_ON_ORDER} نقاط!\n\n"
        "سيتواصل معك فريقنا قريباً.",
        parse_mode="HTML",
        reply_markup=main_keyboard(admin),
    )

    # إشعار الأدمن
    username = message.from_user.username
    admin_text = (
        f"📦 <b>طلب جديد #{order_id}</b>\n\n"
        f"👤 {message.from_user.full_name} (@{username or 'بدون'})\n"
        f"🆔 {user_id}\n\n"
        f"🔧 <b>الخدمة:</b> {data['service']}\n"
        f"📝 <b>التفاصيل:</b>\n{data['details']}\n\n"
        f"💰 <b>الميزانية:</b> {data['budget']}"
    )
    await notify_admin(bot, admin_text, order_actions_inline(order_id))


# ══════════════════════════════════════════════════════════════
# طلباتي
# ══════════════════════════════════════════════════════════════

@router.message(F.text == "📋 طلباتي")
async def show_my_orders(message: Message):
    await ensure_user(message)
    orders = await db.get_user_orders(message.from_user.id)
    if not orders:
        await message.answer("📭 لا توجد طلبات بعد. أنشئ طلبك الأول!")
        return

    STATUS_AR = {
        "pending":    "⏳ قيد الانتظار",
        "processing": "⚙️ قيد التنفيذ",
        "completed":  "✅ مكتمل",
        "rejected":   "❌ مرفوض",
        "cancelled":  "🚫 ملغى",
    }

    text = "📋 <b>طلباتك الأخيرة:</b>\n\n"
    for o in orders[:5]:
        status = STATUS_AR.get(o["status"], o["status"])
        text += (
            f"🔢 <b>#{o['id']}</b> — {o['service_type']}\n"
            f"   الحالة: {status}\n"
            f"   التاريخ: {db.format_date(o['created_at'])}\n\n"
        )
    await message.answer(text, parse_mode="HTML")


# ══════════════════════════════════════════════════════════════
# الدعم الفني - تذاكر (FSM)
# ══════════════════════════════════════════════════════════════

@router.message(F.text == "🎫 الدعم الفني")
async def support_start(message: Message, state: FSMContext):
    user = await ensure_user(message)
    if not user:
        return

    open_count = await db.count_user_open_tickets(message.from_user.id)
    if open_count >= config.MAX_TICKETS_OPEN:
        await message.answer(
            f"⚠️ لديك {open_count} تذاكر مفتوحة. انتظر الرد قبل فتح تذكرة جديدة."
        )
        return

    await state.set_state(TicketState.subject)
    await message.answer(
        "🎫 <b>تذكرة دعم جديدة</b>\n\nما موضوع مشكلتك؟",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="❓ استفسار"), KeyboardButton(text="🐛 مشكلة تقنية")],
                [KeyboardButton(text="💳 مشكلة دفع"), KeyboardButton(text="📦 متابعة طلب")],
                [KeyboardButton(text="❌ إلغاء")],
            ],
            resize_keyboard=True,
        ),
    )


@router.message(TicketState.subject)
async def ticket_subject(message: Message, state: FSMContext):
    if message.text == "❌ إلغاء":
        await state.clear()
        await go_home(message, state)
        return
    await state.update_data(subject=message.text)
    await state.set_state(TicketState.message)
    await message.answer(
        f"📌 الموضوع: <b>{message.text}</b>\n\nاشرح مشكلتك بالتفصيل:",
        parse_mode="HTML",
        reply_markup=cancel_keyboard(),
    )


@router.message(TicketState.message)
async def ticket_message(message: Message, state: FSMContext):
    if message.text == "❌ إلغاء":
        await state.clear()
        await go_home(message, state)
        return
    await state.update_data(message_text=message.text)
    data = await state.get_data()
    await state.set_state(TicketState.confirm)
    await message.answer(
        f"📋 <b>ملخص تذكرتك:</b>\n\n"
        f"📌 الموضوع: {data['subject']}\n"
        f"📝 الرسالة: {message.text}\n\n"
        "تأكيد الإرسال؟",
        parse_mode="HTML",
        reply_markup=confirm_keyboard(),
    )


@router.message(TicketState.confirm)
async def ticket_confirm(message: Message, state: FSMContext, bot: Bot):
    if message.text == "❌ إلغاء":
        await state.clear()
        await go_home(message, state)
        return
    if message.text != "✅ تأكيد":
        return

    data = await state.get_data()
    user_id = message.from_user.id
    ticket_id = await db.create_ticket(user_id, data["subject"], data["message_text"])
    await state.clear()

    if not ticket_id:
        await message.answer("❌ فشل إنشاء التذكرة، حاول مجدداً.")
        return

    admin = is_admin(user_id)
    await message.answer(
        f"✅ <b>تم إرسال تذكرتك!</b>\n"
        f"🔢 رقم التذكرة: <code>#{ticket_id}</code>\n"
        "سيرد عليك فريق الدعم قريباً.",
        parse_mode="HTML",
        reply_markup=main_keyboard(admin),
    )

    username = message.from_user.username
    admin_text = (
        f"🎫 <b>تذكرة جديدة #{ticket_id}</b>\n\n"
        f"👤 {message.from_user.full_name} (@{username or 'بدون'})\n"
        f"🆔 {user_id}\n\n"
        f"📌 <b>الموضوع:</b> {data['subject']}\n"
        f"📝 <b>الرسالة:</b>\n{data['message_text']}"
    )
    await notify_admin(bot, admin_text, ticket_actions_inline(ticket_id))


# ══════════════════════════════════════════════════════════════
# لوحة الأدمن
# ══════════════════════════════════════════════════════════════

@router.message(F.text == "🔐 لوحة الأدمن")
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("🚫 غير مصرح.")
        return
    stats = await db.get_dashboard_stats()
    text = (
        "🔐 <b>لوحة الأدمن</b>\n\n"
        f"👥 المستخدمين: <b>{stats.get('total_users', 0)}</b>\n"
        f"📦 إجمالي الطلبات: <b>{stats.get('total_orders', 0)}</b>\n"
        f"⏳ طلبات اليوم: <b>{stats.get('today_orders', 0)}</b>\n"
        f"🎫 تذاكر مفتوحة: <b>{stats.get('open_tickets', 0)}</b>\n"
        f"🖼️ المعرض: <b>{stats.get('portfolio_count', 0)}</b> مشروع"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=admin_keyboard())


@router.message(F.text == "📊 الإحصائيات")
async def admin_stats(message: Message):
    if not is_admin(message.from_user.id):
        return
    stats  = await db.get_dashboard_stats()
    weekly = await db.get_weekly_orders()
    monthly = await db.get_monthly_stats()

    by_status = stats.get("orders_by_status", {})
    text = (
        "📊 <b>إحصائيات تفصيلية</b>\n\n"
        f"👥 المستخدمين: {stats.get('total_users', 0)}\n\n"
        "<b>الطلبات:</b>\n"
        f"  ⏳ انتظار:   {by_status.get('pending', 0)}\n"
        f"  ⚙️ تنفيذ:    {by_status.get('processing', 0)}\n"
        f"  ✅ مكتمل:   {by_status.get('completed', 0)}\n"
        f"  ❌ مرفوض:   {by_status.get('rejected', 0)}\n\n"
        f"<b>الشهر الحالي:</b>\n"
        f"  🛒 طلبات: {monthly.get('monthly_orders', 0)}\n"
        f"  👤 مستخدمين جدد: {monthly.get('new_users', 0)}\n"
        f"  💵 إيرادات متوقعة: {monthly.get('estimated_revenue', 0)}$\n\n"
        f"<b>آخر 7 أيام:</b>\n"
    )
    if weekly:
        for row in weekly:
            text += f"  📅 {row['date']}: {row['count']} طلبات\n"
    else:
        text += "  لا توجد بيانات\n"

    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "📋 الطلبات المعلقة")
async def admin_pending_orders(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    orders = await db.get_orders_by_status("pending", limit=10)
    if not orders:
        await message.answer("✅ لا توجد طلبات معلقة.")
        return
    await message.answer(f"📋 <b>{len(orders)} طلبات معلقة:</b>", parse_mode="HTML")
    for o in orders:
        text = (
            f"🔢 <b>#{o['id']}</b> — {o['service_type']}\n"
            f"👤 {o.get('full_name', o['user_id'])}\n"
            f"💰 {o.get('budget', '-')}\n"
            f"📝 {str(o.get('details', ''))[:100]}..."
        )
        await message.answer(text, parse_mode="HTML", reply_markup=order_actions_inline(o["id"]))


@router.message(F.text == "🎫 التذاكر المفتوحة")
async def admin_open_tickets(message: Message):
    if not is_admin(message.from_user.id):
        return
    tickets = await db.get_all_open_tickets(limit=10)
    if not tickets:
        await message.answer("✅ لا توجد تذاكر مفتوحة.")
        return
    await message.answer(f"🎫 <b>{len(tickets)} تذاكر:</b>", parse_mode="HTML")
    for t in tickets:
        text = (
            f"🔢 <b>#{t['id']}</b> — {t.get('subject', 'دعم')}\n"
            f"👤 {t.get('full_name', t['user_id'])}\n"
            f"📝 {str(t.get('message', ''))[:80]}..."
        )
        await message.answer(text, parse_mode="HTML", reply_markup=ticket_actions_inline(t["id"]))


@router.message(F.text == "👥 المستخدمين")
async def admin_users(message: Message):
    if not is_admin(message.from_user.id):
        return
    users = await db.get_all_users(limit=10)
    if not users:
        await message.answer("لا يوجد مستخدمين.")
        return
    text = "👥 <b>آخر المستخدمين:</b>\n\n"
    for u in users:
        blocked = " 🚫" if u.get("is_blocked") else ""
        text += (
            f"🆔 {u['id']}{blocked}\n"
            f"   {u.get('full_name', '-')} (@{u.get('username', '-')})\n"
            f"   💎 {u.get('loyalty_points', 0)} نقطة\n\n"
        )
    await message.answer(text, parse_mode="HTML")


# ══════════════════════════════════════════════════════════════
# Callbacks إجراءات الأدمن
# ══════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("order_"))
async def handle_order_action(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("🚫 غير مصرح.", show_alert=True)
        return

    parts  = callback.data.split("_")
    action = parts[1]
    order_id = int(parts[2])
    order  = await db.get_order_by_id(order_id)
    if not order:
        await callback.answer("❌ الطلب غير موجود.", show_alert=True)
        return

    STATUS_MAP = {
        "accept":     ("completed",  "✅ تم قبول طلبك وإكماله!"),
        "processing": ("processing", "⚙️ بدأنا العمل على طلبك!"),
        "reject":     ("rejected",   "❌ عذراً، تم رفض طلبك."),
    }

    if action == "note":
        await state.update_data(target_order_id=order_id, target_user_id=order["user_id"])
        await state.set_state(AdminState.order_notes)
        await callback.message.answer(
            f"📝 اكتب ملاحظتك على الطلب #{order_id}:"
        )
        await callback.answer()
        return

    if action in STATUS_MAP:
        new_status, user_msg = STATUS_MAP[action]
        await db.update_order_status(order_id, new_status)
        await callback.answer(f"✅ تم تحديث الطلب #{order_id}", show_alert=True)
        try:
            await bot.send_message(
                order["user_id"],
                f"📦 <b>تحديث طلبك #{order_id}</b>\n\n{user_msg}",
                parse_mode="HTML",
            )
        except Exception:
            pass
        await callback.message.edit_reply_markup(reply_markup=None)


@router.message(AdminState.order_notes)
async def save_order_notes(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    order_id = data.get("target_order_id")
    user_id  = data.get("target_user_id")
    await db.update_order_notes(order_id, message.text)
    await state.clear()
    await message.answer(f"✅ تم إضافة الملاحظة على الطلب #{order_id}.")
    try:
        await bot.send_message(
            user_id,
            f"💬 <b>ملاحظة جديدة على طلبك #{order_id}</b>\n\n{message.text}",
            parse_mode="HTML",
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("ticket_"))
async def handle_ticket_action(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("🚫 غير مصرح.", show_alert=True)
        return

    parts     = callback.data.split("_")
    action    = parts[1]
    ticket_id = int(parts[2])

    if action == "close":
        await db.update_ticket_status(ticket_id, "closed")
        await callback.answer(f"✅ تم إغلاق التذكرة #{ticket_id}", show_alert=True)
        await callback.message.edit_reply_markup(reply_markup=None)
        return

    if action == "reply":
        ticket = await db.get_ticket_by_id(ticket_id)
        if not ticket:
            await callback.answer("❌ التذكرة غير موجودة.", show_alert=True)
            return
        await state.update_data(
            target_ticket_id=ticket_id,
            target_user_id=ticket["user_id"],
        )
        await state.set_state(AdminState.reply_ticket)
        await callback.message.answer(f"💬 اكتب ردك على التذكرة #{ticket_id}:")
        await callback.answer()


@router.message(AdminState.reply_ticket)
async def send_ticket_reply(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    data      = await state.get_data()
    ticket_id = data.get("target_ticket_id")
    user_id   = data.get("target_user_id")

    await db.add_ticket_reply(ticket_id, config.ADMIN_ID, message.text, is_admin=True)
    await db.update_ticket_status(ticket_id, "in_progress")
    await state.clear()
    await message.answer(f"✅ تم إرسال الرد على التذكرة #{ticket_id}.")

    try:
        await bot.send_message(
            user_id,
            f"💬 <b>رد على تذكرتك #{ticket_id}</b>\n\n"
            f"👨‍💼 <b>فريق الدعم:</b>\n{message.text}",
            parse_mode="HTML",
        )
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════
# البث
# ══════════════════════════════════════════════════════════════

@router.message(F.text == "📢 بث رسالة")
async def broadcast_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.set_state(AdminState.broadcast)
    await message.answer(
        "📢 اكتب رسالة البث (HTML مدعوم):\n\n"
        "(سيتم إرسالها لجميع المستخدمين)",
        reply_markup=cancel_keyboard(),
    )


@router.message(AdminState.broadcast)
async def broadcast_send(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    if message.text == "❌ إلغاء":
        await state.clear()
        await go_home(message, state)
        return

    broadcast_text = message.text
    user_ids = await db.get_all_user_ids()
    await state.clear()
    await message.answer(
        f"📤 بدء إرسال البث لـ {len(user_ids)} مستخدم...",
        reply_markup=admin_keyboard(),
    )

    sent, failed = 0, 0
    for uid in user_ids:
        try:
            await bot.send_message(uid, broadcast_text, parse_mode="HTML")
            sent += 1
            await asyncio.sleep(0.05)  # تجنب الـ flood limit
        except Exception:
            failed += 1

    await db.log_broadcast(broadcast_text, sent, config.ADMIN_ID)
    await message.answer(
        f"✅ <b>اكتمل البث</b>\n✅ أُرسل: {sent}\n❌ فشل: {failed}",
        parse_mode="HTML",
    )


# ══════════════════════════════════════════════════════════════
# أوامر /admin
# ══════════════════════════════════════════════════════════════

@router.message(Command("block"))
async def cmd_block(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("⚠️ الاستخدام: /block <user_id>")
        return
    try:
        uid = int(parts[1])
        await db.block_user(uid, True)
        await message.answer(f"🚫 تم حظر المستخدم {uid}.")
    except ValueError:
        await message.answer("❌ معرف غير صحيح.")


@router.message(Command("unblock"))
async def cmd_unblock(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("⚠️ الاستخدام: /unblock <user_id>")
        return
    try:
        uid = int(parts[1])
        await db.block_user(uid, False)
        await message.answer(f"✅ تم رفع الحظر عن {uid}.")
    except ValueError:
        await message.answer("❌ معرف غير صحيح.")


@router.message(Command("addpoints"))
async def cmd_add_points(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer("⚠️ الاستخدام: /addpoints <user_id> <amount>")
        return
    try:
        uid    = int(parts[1])
        amount = int(parts[2])
        await db.add_points(uid, amount, "admin_grant")
        await message.answer(f"✅ تمت إضافة {amount} نقطة للمستخدم {uid}.")
    except ValueError:
        await message.answer("❌ قيم غير صحيحة.")


# ══════════════════════════════════════════════════════════════
# تسجيل الـ Handlers
# ══════════════════════════════════════════════════════════════

def register_handlers(dp: Dispatcher) -> None:
    dp.include_router(router)
