import random
import string
from flask_sqlalchemy import SQLAlchemy

# 1. تعريف الكائن المركزي (بدون استيراد موديلات هنا لمنع الدوران)
db = SQLAlchemy()

def generate_mah_wallet():
    """توليد معرف محفظة احترافي وعشوائي"""
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(random.choices(chars, k=10))
    return f"MAH-{suffix}"

def init_db(app):
    """تهيئة قاعدة البيانات وربطها بالتطبيق"""
    db.init_app(app)
    
    # لا نضع منطق الحقن هنا مباشرة لمنع التعليق
    with app.app_context():
        db.create_all()
        print("🚀 قاعدة بيانات 'سوقك الذكي' متصلة وجاهزة.")
