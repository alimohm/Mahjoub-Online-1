import os

class Config:
    # جلب رابط قاعدة البيانات من Railway أو استخدام SQLite محلياً كخطة بديلة
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # تصحيح البريد لضمان التوافق مع Postgres على السيرفرات السحابية
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    # حماية الجلسات والمحفظة بمفتاح سري قوي
    SECRET_KEY = os.environ.get('SECRET_KEY', 'MAHJOUB_ROYAL_SECRET_2026')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
