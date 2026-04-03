import random
import string
import datetime
from flask_sqlalchemy import SQLAlchemy

# تعريف الكائن المركزي لقاعدة البيانات
db = SQLAlchemy()

def generate_mah_wallet():
    """توليد معرف محفظة احترافي وعشوائي (10 رموز) للمنصة اللامركزية"""
    # نستخدم الحروف الكبيرة والأرقام ليعطي طابعاً بنكياً قوياً (MAH-XXXXX)
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(random.choices(chars, k=10))
    return f"MAH-{suffix}"

def init_db(app):
    """
    تهيئة قاعدة البيانات، وتأمين حسابات السيادة (علي محجوب).
    """
    from models import Vendor, Product, AdminUser # استيراد الموديلات
    
    db.init_app(app)
    
    with app.app_context():
        try:
            # --- ملاحظة سيادية من علي محجوب ---
            # إذا كنت تريد مسح كل شيء للبدء من جديد (Reset)، ابقِ السطر التالي:
            # db.drop_all() 
            
            db.create_all()
            
            # --- التأكد من وجود حسابك الشخصي (الأدمن والمورد الأول) ---
            admin_vendor = Vendor.query.filter_by(username="ali").first()
            if not admin_vendor:
                random_wallet = generate_mah_wallet()
                
                new_admin = Vendor(
                    username="ali", 
                    password="123", # يرجى تغييره لاحقاً للأمان
                    brand_name="محجوب أونلاين | سوقك الذكي",
                    employee_name="علي محجوب",
                    phone_number="777000000",
                    wallet_address=random_wallet,
                    balance=0.0,
                    is_active=True # حسابك دائماً نشط سيادياً
                )
                db.session.add(new_admin)
                db.session.commit()
                print(f"👤 تم تفعيل حساب السيادة (علي محجوب)! المحفظة: {random_wallet}")
            
            print("🚀 قاعدة بيانات 'سوقك الذكي' متصلة ومستعدة لاعتماد الموردين!")
            
        except Exception as e:
            print(f"❌ خطأ تقني في قاعدة البيانات: {e}")
