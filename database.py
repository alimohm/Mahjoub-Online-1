import os
from flask_sqlalchemy import SQLAlchemy

# تعريف كائن قاعدة البيانات
db = SQLAlchemy()

def init_db(app):
    """
    تهيئة الاتصال بقاعدة البيانات باستخدام الرابط من بيئة ريلوي
    """
    # جلب رابط قاعدة البيانات من المتغيرات البيئية في ريلوي
    db_url = os.environ.get('DATABASE_URL')
    
    # تصحيح الرابط ليتوافق مع SQLAlchemy (تحويل postgres إلى postgresql)
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # ربط التطبيق بقاعدة البيانات
    db.init_app(app)

class Vendor(db.Model):
    """
    تعريف جدول الموردين مطابقاً لما هو موجود في قاعدة بياناتك
    """
    __tablename__ = 'vendor'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    owner_name = db.Column(db.String(100))
    wallet_address = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<Vendor {self.username}>'
