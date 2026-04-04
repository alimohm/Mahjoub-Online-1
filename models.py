import random
import string
from datetime import datetime
from werkzeug.security import generate_password_hash
from database import db 

def generate_mah_wallet():
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"MAH-{suffix}"

class Vendor(db.Model):
    __tablename__ = 'vendor'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False) 
    employee_name = db.Column(db.String(120)) 
    brand_name = db.Column(db.String(120), nullable=False)    
    phone_number = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True) 
    status = db.Column(db.String(30), default='active') 
    wallet_address = db.Column(db.String(255), unique=True, default=generate_mah_wallet)
    products = db.relationship('Product', backref='vendor_owner', lazy=True)

class AdminUser(db.Model):
    __tablename__ = 'admin_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def seed_admin():
    """حقن البيانات لضمان دخولك الفوري بكلمة مرور 123"""
    try:
        secure_pw = generate_password_hash('123')
        
        # 🏛️ حساب الإدارة (برج المراقبة)
        # غيرنا الاسم لـ ali_admin لتفادي مشاكل الحروف العربية في تسجيل الدخول
        admin = AdminUser.query.filter_by(username='ali_admin').first()
        if not admin:
            new_admin = AdminUser(username='ali_admin', password=secure_pw)
            db.session.add(new_admin)
        
        # 📦 حساب المورد (المنصة اللامركزية)
        vendor = Vendor.query.filter_by(username='ali_mahjoub').first()
        if not vendor:
            new_vendor = Vendor(
                username='ali_mahjoub', 
                password=secure_pw, 
                brand_name='Mahjoub Online', 
                status='active'
            )
            db.session.add(new_vendor)
            
        db.session.commit()
        print("✅ تم تحديث بيانات الدخول: ali_admin و ali_mahjoub جاهزان.")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Seed Error: {e}")
