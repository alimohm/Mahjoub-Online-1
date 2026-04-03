import random
import string
from datetime import datetime
from database import db
from werkzeug.security import generate_password_hash

def generate_mah_wallet():
    """توليد عنوان محفظة فريد يبدأ بـ MAH متبوع بـ 10 رموز"""
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"MAH-{suffix}"

class Vendor(db.Model):
    """جدول الموردين والموظفين - الكيان اللامركزي لمحجوب أونلاين"""
    __tablename__ = 'vendor'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # بيانات الدخول للمورد
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False) # تم زيادة الطول لاستيعاب التشفير
    
    # الحقول التشغيلية والمعلومات الشخصية
    employee_name = db.Column(db.String(120), nullable=True) 
    brand_name = db.Column(db.String(120), nullable=False)    
    phone_number = db.Column(db.String(20), nullable=True)
    
    # --- صلاحيات المدير العام والحالات السيادية ---
    is_active = db.Column(db.Boolean, default=True) 
    status = db.Column(db.String(30), default='active') # active, blocked, restricted, pending, under_surveillance
    
    # الهوية الرقمية اللامركزية للمؤسسة
    wallet_address = db.Column(db.String(255), unique=True, default=generate_mah_wallet)
    
    # توكن الربط الخارجي
    qomra_access_token = db.Column(db.Text, nullable=True)
    
    # علاقة المنتجات
    products = db.relationship('Product', backref='vendor_owner', lazy=True)

    def __repr__(self):
        return f'<Vendor: {self.employee_name} | Brand: {self.brand_name}>'

class Product(db.Model):
    """جدول المنتجات - قلب منصة محجوب أونلاين اللامركزية"""
    __tablename__ = 'product'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    brand = db.Column(db.String(120), nullable=True)  
    
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='YER') 
    stock = db.Column(db.Integer, default=1)           
    
    # المحتوى والوسائط
    description = db.Column(db.Text)
    image_file = db.Column(db.Text) 
    
    # --- حقول التحكم الإداري (علي محجوب) ---
    status = db.Column(db.String(20), default='pending') # pending, approved, rejected
    is_published = db.Column(db.Boolean, default=False)
    
    # الربط التقني
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id')) 
    vendor_username = db.Column(db.String(80))                    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name} - Status: {self.status}>'

class AdminUser(db.Model):
    """جدول الإدارة المركزية - برج المراقبة"""
    __tablename__ = 'admin_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False) # تم زيادة الطول لاستيعاب التشفير

# --- دالة حقن البيانات المحدثة (تأمين الهوية) ---
def seed_admin():
    """تأكد من وجود حسابات الإدارة والموردين مشفرة وجاهزة"""
    
    # تشفير كلمة المرور الافتراضية
    secure_password = generate_password_hash('123')

    # 1. تحديث حساب المدير العام (برج المراقبة)
    admin = AdminUser.query.filter_by(username='علي محجوب').first()
    if not admin:
        new_admin = AdminUser(username='علي محجوب', password=secure_password)
        db.session.add(new_admin)
        db.session.commit()
        print("✅ تم تفعيل حساب المدير العام المشفر: علي محجوب")

    # 2. إضافة علي محجوب كمورد (Vendor) مع الحالة النشطة
    vendor = Vendor.query.filter_by(username='ali_mahjoub').first()
    if not vendor:
        new_vendor = Vendor(
            username='ali_mahjoub',
            password=secure_password,
            employee_name='علي محجوب',
            brand_name='Mahjoub Online',
            phone_number='777777777',
            status='active' # الحالة الافتراضية للبدء
        )
        db.session.add(new_vendor)
        db.session.commit()
        print("✅ تم إضافة حساب المورد المشفر: ali_mahjoub")
