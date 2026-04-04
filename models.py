import string
import random
from database import db
from datetime import datetime

# دالة توليد رقم المحفظة الفريد (MAH-XXXXXXXX)
def generate_wallet_id():
    # اختيار حروف كبيرة وأرقام بطول 8 رموز
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
    status = db.Column(db.String(50), default="نشط")
    is_active = db.Column(db.Boolean, default=True)
    
    # الربط مع الموظفين والمحفظة
    staff = db.relationship('VendorStaff', backref='owner', lazy=True)
    wallet = db.relationship('Wallet', backref='vendor_ref', uselist=False, cascade="all, delete-orphan")

# --- [ 3. جدول موظفي المورد ] ---
class VendorStaff(db.Model):
    __tablename__ = 'vendor_staff'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    national_id = db.Column(db.String(100), nullable=False)

# --- [ 4. جدول المحفظة ] ---
class Wallet(db.Model):
    __tablename__ = 'wallet'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), unique=True, nullable=False)
    # رقم المحفظة المميز الذي يبدأ بـ MAH-
    wallet_number = db.Column(db.String(20), unique=True, default=generate_wallet_id)
    balance = db.Column(db.Float, default=0.0)
    pending_balance = db.Column(db.Float, default=0.0)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)

# --- [ 5. دالة حقن البيانات وتجهيز الحسابات ] ---
def seed_system():
    # 1. إضافة الإدارة (علي)
    if not AdminUser.query.filter_by(username="علي").first():
        db.session.add(AdminUser(username="علي", password="123", role="Super Admin"))
    
    # 2. إضافة المورد (علي محمد)
    vendor_acc = Vendor.query.filter_by(username="علي محمد").first()
    if not vendor_acc:
        vendor_acc = Vendor(username="علي محمد", password="123", brand_name="محجوب أونلاين")
        db.session.add(vendor_acc)
        db.session.commit() # الحفظ للحصول على ID

    # 3. توليد المحفظة تلقائياً للمورد بكود MAH-
    if vendor_acc and not Wallet.query.filter_by(vendor_id=vendor_acc.id).first():
        new_wallet = Wallet(vendor_id=vendor_acc.id)
        db.session.add(new_wallet)
        print(f"✅ تم توليد محفظة برقم: {new_wallet.wallet_number} للمورد: {vendor_acc.username}")

    # 4. إضافة الموظف التجريبي
    if not VendorStaff.query.filter_by(username="الموظف التجريبي").first():
        if vendor_acc:
            db.session.add(VendorStaff(
                username="الموظف التجريبي", 
                password="123", 
                national_id="EXP-123", 
                vendor_id=vendor_acc.id
            ))

    db.session.commit()
    print("✨ تم تحديث النظام بنجاح مع أرقام المحفظة الجديدة.")
