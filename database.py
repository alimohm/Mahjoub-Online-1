import random
import string
import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash # استيراد التشفير الضروري

# تعريف الكائن المركزي لقاعدة البيانات
db = SQLAlchemy()

def generate_mah_wallet():
    """توليد معرف محفظة احترافي وعشوائي للمنصة اللامركزية"""
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(random.choices(chars, k=10))
    return f"MAH-{suffix}"

def init_db(app):
    """
    تهيئة قاعدة البيانات، وتأمين حسابات السيادة (علي محجوب) بالتشفير.
    """
    from models import Vendor, Product, AdminUser # استيراد الموديلات
    
    db.init_app(app)
    
    with app.app_context():
        try:
            # لضمان تحديث الجداول بالحقول الجديدة (مثل status)، يفضل مسح القاعدة مرة واحدة
            # db.drop_all() 
            
            db.create_all()
            
            # --- تأمين كلمة المرور سيادياً (تشفير 123) ---
            secure_password = generate_password_hash("123")
            
            # 1. التأكد من وجود حسابك كـ (Vendor)
            admin_vendor = Vendor.query.filter_by(username="ali").first()
            if not admin_vendor:
                random_wallet = generate_mah_wallet()
                
                new_admin_v = Vendor(
                    username="ali", 
                    password=secure_password, # تخزين الشفرة وليس النص
                    brand_name="محجوب أونلاين | سوقك الذكي",
                    employee_name="علي محجوب",
                    phone_number="777000000",
                    wallet_address=random_wallet,
                    status="active", # الحالة السيادية نشطة
                    is_active=True 
                )
                db.session.add(new_admin_v)
                print(f"👤 تم تفعيل حساب المورد السيادي (علي محجوب)!")

            # 2. التأكد من وجود حسابك كـ (Admin) في برج المراقبة
            admin_user = AdminUser.query.filter_by(username="علي محجوب").first()
            if not admin_user:
                new_admin_u = AdminUser(
                    username="علي محجوب",
                    password=secure_password # استخدام نفس الشفرة للأدمن
                )
                db.session.add(new_admin_u)
                print(f"🏰 تم تفعيل حساب برج المراقبة (علي محجوب)!")

            db.session.commit()
            print("🚀 قاعدة بيانات 'سوقك الذكي' متصلة ومؤمنة بالتشفير الرقمي!")
            
        except Exception as e:
            print(f"❌ خطأ تقني في قاعدة البيانات: {e}")
