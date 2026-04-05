import string
import random
from database import db
from datetime import datetime

# دالة توليد رقم المحفظة الفريد (MAH-XXXXXXXX)
def generate_wallet_id():
    chars = string.ascii_uppercase + string.digits
    random_code = ''.join(random.choices(chars, k=8))
    return f"MAH-{random_code}"

# --- [ 1. جدول الإدارة العليا ] ---
class AdminUser(db.Model):
    __tablename__ = 'admin_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default="Super Admin")

# --- [ 2. جدول الموردين ] ---
class Vendor(db.Model):
    __tablename__ = 'vendor' # تأكد من أن الاسم مفرد كما في الصورة السابقة
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    brand_name = db.Column(db.String(150))
    status = db.Column(db.String(50), default="نشط")
    is_active = db.Column(db.Boolean, default=True)
    
    # علاقات الربط
    staff = db.relationship('VendorStaff', backref='owner', lazy=True)
    wallet = db.relationship('Wallet', backref='vendor_ref', uselist=False, cascade="all, delete-orphan")
    # إضافة علاقة مع المنتجات لتسهيل جلبها في الداشبورد
    products = db.relationship('Product', backref='vendor_info', lazy=True)

# --- [ 3. جدول موظفي المورد ] ---
class VendorStaff(db.Model):
    __tablename__ = 'vendor_staff'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    national_id = db.Column(db.String(100), nullable=False)

    # إضافة علاقة عكسية للوصول للمورد بسهولة
    vendor = db.relationship('Vendor', backref=db.backref('staff_members', lazy=True))

# --- [ 4. جدول المحفظة ] ---
class Wallet(db.Model):
    __tablename__ = 'wallet'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), unique=True, nullable=False)
    wallet_number = db.Column(db.String(20), unique=True, default=generate_wallet_id)
    balance = db.Column(db.Float, default=0.0)
    pending_balance = db.Column(db.Float, default=0.0)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)

# --- [ 5. جدول المنتجات - تم تصحيح الربط هنا ] ---
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    brand = db.Column(db.String(100))
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='YER')
    stock = db.Column(db.Integer, default=1)
    description = db.Column(db.Text)
    media_path = db.Column(db.String(500))
    status = db.Column(db.String(20), default='pending') 
    
    # تصحيح الخطأ: كان يشير لـ 'vendors.id' بينما اسم الجدول هو 'vendor'
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name}>'

# --- [ 6. دالة حقن البيانات ] ---
def seed_system():
    # التحقق من وجود الإدارة
    if not AdminUser.query.filter_by(username="علي").first():
        db.session.add(AdminUser(username="علي", password="123", role="Super Admin"))
    
    # التحقق من وجود مورد رئيسي
    vendor_acc = Vendor.query.filter_by(username="علي محمد").first()
    if not vendor_acc:
        vendor_acc = Vendor(username="علي محمد", password="123", brand_name="محجوب أونلاين")
        db.session.add(vendor_acc)
        db.session.commit()

    # توليد المحفظة إذا لم توجد
    if vendor_acc and not Wallet.query.filter_by(vendor_id=vendor_acc.id).first():
        new_wallet = Wallet(vendor_id=vendor_acc.id)
        db.session.add(new_wallet)
        print(f"✅ محفظة سيادية جديدة: {new_wallet.wallet_number}")

    db.session.commit()
