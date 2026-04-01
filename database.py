import os
import random
import string
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    owner_name = db.Column(db.String(120))
    brand_name = db.Column(db.String(120)) # سيتم توليده تلقائياً
    brand_logo_url = db.Column(db.String(255))
    wallet_address = db.Column(db.String(255), unique=True) # رقم المحفظة الفريد

def generate_mq_wallet():
    """توليد رقم محفظة سيادي يبدأ بـ MQ متبوعاً بـ 8 رموز"""
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choice(chars) for _ in range(8))
    return f"MQ-{code}"

def init_db(app):
    uri = os.environ.get('DATABASE_URL')
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    app.config.update(
        SQLALCHEMY_DATABASE_URI=uri or 'sqlite:///local.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY=os.environ.get('SK', 'MAHJOUB_2026')
    )
    
    db.init_app(app)
    
    with app.app_context():
        # تنبيه: هذا يمسح البيانات القديمة لإصلاح الهيكل
        db.drop_all() 
        db.create_all()
        
        # إنشاء حسابك 'ali' مع بيانات تلقائية ذكية
        if not Vendor.query.filter_by(username='ali').first():
            ali_user = "ali"
            new_v = Vendor(
                username=ali_user,
                password='123',
                phone='77xxxxxxx',
                owner_name='علي محجوب',
                # توليد اسم العلامة تلقائياً إذا لم يتوفر
                brand_name=f"متجر {ali_user}", 
                # توليد رقم محفظة MQ تلقائي
                wallet_address=generate_mq_wallet()
            )
            db.session.add(new_v)
            db.session.commit()
