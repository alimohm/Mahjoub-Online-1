import os

class Config:
    """
    إعدادات منصة محجوب أونلاين - الهوية الرقمية 2026
    تم ضبط هذا الملف ليعمل بذكاء بين البيئة المحلية وبيئة السيرفر (Railway).
    """
    
    # 1. سر التشفير للجلسات (المفتاح الملكي الخاص بك)
    # يحاول القراءة من متغيرات البيئة 'SK'، وإذا لم يجدها يستخدم القيمة الافتراضية.
    SECRET_KEY = os.environ.get('SK', 'MAHJOUB_ROYAL_2026')
    
    # 2. الربط الذكي بقاعدة البيانات
    # نقرأ رابط قاعدة البيانات من Railway
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # تصحيح بروتوكول Postgres ليتوافق مع SQLAlchemy الحديثة
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # خطة بديلة (Fallback): إذا كنت تشغل الكود على جهازك الشخصي
        # سيتم إنشاء قاعدة بيانات محلية باسم mahjoub_local.db لضمان عدم توقف النظام.
        SQLALCHEMY_DATABASE_URI = 'sqlite:///mahjoub_local.db'
    
    # تعطيل نظام التتبع لزيادة سرعة الأداء وتوفير موارد السيرفر
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- 3. إعدادات الميديا والرفع اللامركزي ---
    
    # تحديد مسار مجلد الصور في static
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    
    # تحديد الحجم الأقصى للصورة (16 ميجا بايت) لضمان دقة عرض المنتجات
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 

    # أنواع الملفات المسموح برفعها لضمان أمن المنصة
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
