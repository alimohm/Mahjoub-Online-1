import random
import string
from flask_sqlalchemy import SQLAlchemy

# تعريف الكائن المركزي لقاعدة البيانات
db = SQLAlchemy()

def generate_mah_wallet():
    """توليد معرف محفظة احترافي وعشوائي (10 رموز)"""
    # نستخدم الحروف الكبيرة والأرقام ليعطي طابعاً بنكياً قوياً
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(random.choices(chars, k=10))
    return f"MAH-{suffix}"

def init_db(app):
    """
    تهيئة قاعدة البيانات، تحديث الهيكل، وإنشاء حساب الأدمن بهوية عشوائية.
    """
    # استيراد الموديلات من ملف models.py لضمان التعرف على الحقول الجديدة
    from models import Vendor, Product 
    
    # ربط Flask بالكائن db
    db.init_app(app)
    
    with app.app_context():
        try:
            # --- المرحلة 1: تصفير وتحديث الهيكل (للمزامنة مع PostgreSQL) ---
            # تنبيه: هذا السطر سيمسح البيانات لمرة واحدة لتطبيق التعديلات الجديدة
            db.drop_all() 
            db.create_all()
            
            # --- المرحلة 2: إنشاء حسابك (الأدمن) بالهوية العشوائية الجديدة ---
            if not Vendor.query.filter_by(username="ali").first():
                # توليد المحفظة العشوائية الآن
                random_wallet = generate_mah_wallet()
                
                admin_user = Vendor(
                    username="ali", 
                    password="123", 
                    brand_name="محجوب أونلاين | سوقك الذكي",
                    wallet_address=random_wallet # هنا سيظهر الرمز العشوائي (10 أحرف)
                )
                db.session.add(admin_user)
                db.session.commit()
                print(f"👤 تم إنشاء مستخدم الأدمن بنجاح! محفظتك: {random_wallet}")
            
            print("🚀 تم تحديث الجداول في PostgreSQL والمنصة جاهزة للانطلاق!")
            
        except Exception as e:
            print(f"❌ حدث خطأ أثناء تهيئة قاعدة البيانات: {e}")

# --- نصيحة المهندس ---
# بمجرد أن ترى المحفظة العشوائية في لوحتك وتتأكد من عمل النظام، 
# قم بوضع علامة # قبل السطر db.drop_all() لحماية بياناتك من المسح مستقبلاً.
