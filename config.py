import os
from dotenv import load_dotenv

# تحميل ملف .env (يعمل في البيئة المحلية فقط)
load_dotenv()

# جلب توكن البوت من إعدادات البيئة في Render
BOT_TOKEN = os.getenv("BOT_TOKEN")

# جلب معرف الأدمن مع وضع قيمة افتراضية (0) لتجنب خطأ التحويل الرقمي
try:
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
except (TypeError, ValueError):
    ADMIN_ID = 0

# روابط قاعدة البيانات والمفاتيح السرية
DATABASE_URL = os.getenv("DATABASE_URL")
API_SECRET_KEY = os.getenv("API_SECRET_KEY")

# ملاحظة للعبقري: تأكد من إضافة هذه الأسماء في 'Environment Variables' على Render

