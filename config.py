import os
from dotenv import load_dotenv

# تحميل ملف .env للمحلي فقط
load_dotenv()

# الإعدادات الأساسية - تأكد من إضافتها في Dashboard الخاص بـ Render
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
API_SECRET_KEY = os.getenv("API_SECRET_KEY", "vexo_secret_123")

# تحويل ADMIN_ID لرقم مع معالجة الأخطاء
try:
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
except (ValueError, TypeError):
    ADMIN_ID = 0

# إعداد المنفذ لـ Render
PORT = int(os.getenv("PORT", 8000))
