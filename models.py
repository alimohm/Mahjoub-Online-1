from database import db
from datetime import datetime
import random

# 1. جدول الإدارة (Admin)
class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True) # مؤندكس للسرعة
    password = db.Column(db.String(128), nullable=False)

# 2. جدول الموردين (Vendors)
class Vendor(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True) # مؤندكس
    brand_name = db.Column(db.String(120), nullable=False, index=True) # مؤندكس للبحث
    password = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20), index=True)
    
    # صور التوثيق
    id_card_image = db.Column(db.String(255))
    commercial_registry_image = db.Column(db.String(255))
    
    # الحالة والتحكم
    status = db.Column(db.String(20), default="معلق", index=True) # مؤندكس للفلترة
    is_active = db.Column(db.Boolean, default=False, index=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # العلاقات
    wallet = db.relationship('Wallet', backref='vendor', uselist=False, cascade="all, delete-orphan")
    products = db.relationship('Product', backref='vendor', lazy=True)
    staff = db.relationship('VendorStaff', backref='vendor', lazy=True)

# 3. جدول المحفظة المالية (Wallet)
class Wallet(db.Model):
    __tablename__ = 'wallets'
    id = db.Column(db.Integer, primary_key=True)
    wallet_number = db.Column(db.String(50), unique=True, nullable=False, index=True) # مؤندكس سيادياً
    balance = db.Column(db.Float, default=0.0)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False, index=True)

    def __init__(self, **kwargs):
        super(Wallet, self).__init__(**kwargs)
        if not self.wallet_number:
            self.wallet_number = f"MAH-{random.randint(1000000, 9999999)}"

# 4. جدول طاقم العمل للمورد (Vendor Staff)
class VendorStaff(db.Model):
    __tablename__ = 'vendor_staff'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default="staff") # مثلاً: محاسب، مدير مخزن
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False, index=True)

# 5. جدول المنتجات (Products)
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True) # مؤندكس لسرعة بحث الزبائن
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(255))
    category = db.Column(db.String(50), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False, index=True)
