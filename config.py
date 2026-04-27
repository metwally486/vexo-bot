"""
config.py — إعدادات Vexo Bot
تحميل جميع المتغيرات من البيئة أو ملف .env (للتطوير المحلي فقط)
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ─── أساسيات البوت ────────────────────────────────────────────
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
DATABASE_URL: str = os.getenv("DATABASE_URL", "")
API_SECRET_KEY: str = os.getenv("API_SECRET_KEY", "vexo_secret_123")

try:
    ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0"))
except (ValueError, TypeError):
    ADMIN_ID = 0

PORT: int = int(os.getenv("PORT", "8000"))

# ─── إعدادات القناة والمجموعة ─────────────────────────────────
CHANNEL_USERNAME: str = os.getenv("CHANNEL_USERNAME", "")   # مثال: @vexo_channel
CHANNEL_ID: int = int(os.getenv("CHANNEL_ID", "0"))          # معرف القناة الرقمي

# ─── نقاط الولاء ──────────────────────────────────────────────
POINTS_ON_JOIN_CHANNEL: int = 50     # نقاط الانضمام للقناة
POINTS_ON_ORDER: int = 10            # نقاط عند إنشاء طلب
POINTS_REDEEM_RATE: int = 100        # كل 100 نقطة = 1$

# ─── قيود وحدود ───────────────────────────────────────────────
MAX_ORDERS_PER_DAY: int = 5          # الحد الأقصى للطلبات اليومية
MAX_TICKETS_OPEN: int = 3            # الحد الأقصى للتذاكر المفتوحة
MAX_PORTFOLIO_ITEMS: int = 50        # الحد الأقصى لعناصر المعرض

# ─── التحقق عند التشغيل ───────────────────────────────────────
def validate_config() -> list[str]:
    """يرجع قائمة بالمتغيرات المفقودة"""
    missing = []
    if not BOT_TOKEN:
        missing.append("BOT_TOKEN")
    if not DATABASE_URL:
        missing.append("DATABASE_URL")
    if not ADMIN_ID:
        missing.append("ADMIN_ID")
    return missing
