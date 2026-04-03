import random
import string
from datetime import datetime
from werkzeug.security import generate_password_hash
from database import db 

def generate_mah_wallet():
    """توليد عنوان محفظة فريد يبدأ بـ MAH"""
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
    status = db.Column(db.String(30), default='active') # إصلاح الحقل المفقود
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
    """حقن بيانات علي محجوب لضمان الدخول بـ 123"""
    secure_pw = generate_password_hash('123')
    # تأمين حساب الإدارة
    if not AdminUser.query.filter_by(username='علي محجوب').first():
        db.session.add(AdminUser(username='علي محجوب', password=secure_pw))
    # تأمين حساب المورد الافتراضي
    if not Vendor.query.filter_by(username='ali_mahjoub').first():
        db.session.add(Vendor(username='ali_mahjoub', password=secure_pw, brand_name='Mahjoub Online', status='active'))
    db.session.commit()
