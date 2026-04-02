from flask_sqlalchemy import SQLAlchemy

# تعريف الكائن المركزي لقاعدة البيانات
db = SQLAlchemy()

def init_db(app):
    """
    تهيئة قاعدة البيانات وربط الموديلات بالهيكل الجديد.
    ملاحظة: سيتم مسح البيانات القديمة لمرة واحدة لضمان عمل الداشبورد.
    """
    # استيراد الموديلات من ملف models.py لضمان التعرف على الحقول الجديدة (is_published)
    from models import Vendor, Product 
    
    # ربط Flask بالكائن db
    db.init_app(app)
    
    with app.app_context():
        try:
            # --- السطر السحري (فك التعليق للمزامنة مع PostgreSQL) ---
            # تنبيه: هذا السطر سيمسح كل البيانات الحالية ليبني الجداول الجديدة
            db.drop_all() 
            
            # إنشاء الجداول بالهيكل المحدث
            db.create_all()
            
            print("🚀 تم تصفير الجداول وإعادة بنائها بالهيكل الجديد في PostgreSQL!")
            print("✅ حقل 'is_published' متاح الآن، والداشبورد سيعمل بنجاح.")
            
        except Exception as e:
            print(f"❌ حدث خطأ أثناء تهيئة PostgreSQL: {e}")

# ملاحظة هامة: بعد تشغيل السيرفر لمرة واحدة ونجاح الدخول للداشبورد،
# قم بوضع علامة # قبل db.drop_all() لكي لا تفقد بيانات الموردين في كل مرة.
