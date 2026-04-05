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
    __tablename__ = 'vendor' 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    brand_name = db.Column(db.String(150))
    
    # --- الإضافات المطلوبة (البيانات الشخصية) ---
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ضبط الحالة لتعمل مع أزرار التفعيل
    status = db.Column(db.String(50), default="معلق")
    is_active = db.Column(db.Boolean, default=False) 
    
    # علاقات الربط
    staff = db.relationship('VendorStaff', back_populates='vendor', lazy=True, overlaps="owner,staff")
    wallet = db.relationship('Wallet', backref='vendor_ref', uselist=False, cascade="all, delete-orphan")
    products = db.relationship('Product', backref='vendor_info', lazy=True)

# --- [ 3. جدول موظفي المورد ] ---
class VendorStaff(db.Model):
    __tablename__ = 'vendor_staff'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    national_id = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True) # إضافة الهاتف للموظف

    vendor = db.relationship('Vendor', back_populates='staff', overlaps="owner,staff")

# --- [ 4. جدول المحفظة ] ---
class Wallet(db.Model):
    __tablename__ = 'wallet'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), unique=True, nullable=False)
    wallet_number = db.Column(db.String(20), unique=True, default=generate_wallet_id)
    balance = db.Column(db.Float, default=0.0)
    pending_balance = db.Column(db.Float, default=0.0)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)

# --- [ 5. جدول المنتجات ] ---
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
    
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name}>'

# --- [ 6. دالة حقن البيانات (Seed) ] ---
def seed_system():
    # 1. التأكد من وجود الإدارة العليا
    if not AdminUser.query.filter_by(username="علي").first():
        db.session.add(AdminUser(username="علي", password="123", role="Super Admin"))
    
    # 2. التأكد من وجود المورد الرئيسي
    vendor_acc = Vendor.query.filter_by(username="علي محمد").first()
    if not vendor_acc:
        vendor_acc = Vendor(
            username="علي محمد", 
            password="123", 
            brand_name="محجوب أونلاين",
            phone="777777777",
            status="نشط",
            is_active=True
        )
        db.session.add(vendor_acc)
        db.session.commit() 

    # 3. التأكد من توليد المحفظة
    if vendor_acc and not Wallet.query.filter_by(vendor_id=vendor_acc.id).first():
        new_wallet = Wallet(vendor_id=vendor_acc.id)
        db.session.add(new_wallet)
        print(f"✅ تم توليد محفظة: {new_wallet.wallet_number}")

    db.session.commit()
