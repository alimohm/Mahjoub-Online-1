import os

class Config:
    # سر التشفير للجلسات (استخدمنا المفتاح الملكي الخاص بك)
    SECRET_KEY = os.environ.get('SK', 'MAHJOUB_ROYAL_2026')
    
    # الربط التلقائي مع Postgres في Railway
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- إعدادات المزامنة والرفع الجديدة ---
    
    # تحديد مسار مجلد الصور الذي أنشأته في static
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    
    # تحديد الحجم الأقصى للصورة (16 ميجا بايت لضمان الجودة)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 

    # أنواع الملفات المسموح بها (أمان إضافي)
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
