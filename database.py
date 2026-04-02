import os
import random
import string
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()

# استيراد النماذج من ملف models (سيتم إنشاؤه في الخطوة التالية)
# ملاحظة: نضعه داخل الدالة لتجنب التعارض
def init_db(app):
    from models import Vendor, Product
    
    uri = os.environ.get('DATABASE_URL')
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = uri or 'sqlite:///local.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        try:
            # 1. إنشاء الجداول الأساسية
            db.create_all()
            
            # 2. نظام الترقيع الذكي لإضافة الأعمدة المطلوبة للمزامنة والاختفاء
            columns_to_check = [
                ("vendor_username", "VARCHAR(80)"),
                ("image_file", "VARCHAR(200)"),
                ("is_published", "BOOLEAN DEFAULT FALSE"), # لضمان اختفاء المنتج بعد نشره
                ("qomra_id", "VARCHAR(100)")                # لربطه بقمرة
            ]
            
            for col_name, col_type in columns_to_check:
                try:
                    db.session.execute(text(f"SELECT {col_name} FROM product LIMIT 1"))
                except Exception:
                    db.session.rollback()
                    print(f"🚀 تحديث سيادي: جاري إضافة عمود {col_name}...")
                    db.session.execute(text(f"ALTER TABLE product ADD COLUMN {col_name} {col_type}"))
                    db.session.commit()

            # 3. التأكد من وجود حسابك (علي) بمحفظة MAH
            from models import generate_mah_wallet
            admin = Vendor.query.filter_by(username='ali').first()
            if not admin:
                admin_user = Vendor(
                    username='ali',
                    password='123',
                    brand_name='محجوب أونلاين',
                    wallet_address=generate_mah_wallet()
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✅ تم إنشاء حساب الأدمن بنجاح.")
                
        except Exception as e:
            print(f"❌ خطأ في تهيئة قاعدة البيانات: {e}")
