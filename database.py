import os
from flask_sqlalchemy import SQLAlchemy

# تعريف كائن قاعدة البيانات السيادي
db = SQLAlchemy()

def init_db(app):
    """
    تهيئة الاتصال بقاعدة البيانات باستخدام الرابط من بيئة ريلوي (Railway)
    """
    # جلب رابط قاعدة البيانات من المتغيرات البيئية
    db_url = os.environ.get('DATABASE_URL')
    
    # تصحيح الرابط ليتوافق مع SQLAlchemy 
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    # إذا لم يوجد رابط (للبيئة المحلية)، نستخدم SQLite مؤقتاً للتجربة
    if not db_url:
        db_url = 'sqlite:///local_vendors.db'
        print("⚠️ تنبيه: يتم استخدام قاعدة بيانات محلية (SQLite)")

    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # ربط التطبيق بقاعدة البيانات
    db.init_app(app)

class Vendor(db.Model):
    """
    تعريف جدول الموردين (قمرة) ليتوافق مع سلاسل الإمداد اللامركزية
    """
    __tablename__ = 'vendor'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    
    # أعمدة إضافية لدعم الهوية المهنية للمورد
    owner_name = db.Column(db.String(100)) # اسم مالك النشاط التجاري
    wallet_address = db.Column(db.String(100)) # لاستلام الأرباح (نظام لا مركزي)
    store_name = db.Column(db.String(100)) # اسم المحل أو الماركة
    
    def __repr__(self):
        return f'<Vendor {self.username} - {self.store_name}>'
