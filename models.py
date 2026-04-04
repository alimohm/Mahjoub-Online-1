from database import db
from datetime import datetime
import uuid
import random
import string

# --- [ 1. جدول الإدارة العليا: علي محجوب ] ---
class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False) # باللغة العربية
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default="Super Admin") # (مالك عام، مدير عمليات، مراقب مالي)
    phone = db.Column(db.String(20), nullable=True)

# --- [ 2. جدول الموردين (المالك الأصلي) ] ---
class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False) # باللغة العربية
    password = db.Column(db.String(200), nullable=False)
    brand_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    
    # الوثائق الرسمية
    doc_type = db.Column(db.String(50)) # (سجل تجاري، مزاولة مهنة، هوية وطنية)
    doc_number = db.Column(db.String(100))
    doc_image = db.Column(db.String(255)) # مسار صورة الوثيقة
    
    # الجغرافيا والسيادة
    address_text = db.Column(db.String(255)) # المحافظة - المديرية
    location_url = db.Column(db.String(500)) # رابط الخريطة
    
    # الحالة والحوكمة
    status = db.Column(db.String(50), default="تحت الرقابة") # (منشط، محظور، مقيد، تحت الرقابة)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # علاقة مع الموظفين والمنتجات
    staff = db.relationship('VendorStaff', backref='owner', lazy=True)
    products = db.relationship('Product', backref='vendor', lazy=True)

# --- [ 3. جدول موظفي المورد ] ---
class VendorStaff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False) # باللغة العربية
    password = db.Column(db.String(200), nullable=False)
    national_id = db.Column(db.String(100), nullable=False) # الهوية الرسمية للموظف
    staff_role = db.Column(db.String(50), default="Full Access") # صلاحيات كاملة عدا المالية

# --- [ 4. جدول المنتجات والمحفظة الذكية ] ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default="YER")
    
    # المحفظة المالية الذكية
    wallet_id = db.Column(db.String(20), unique=True) # يبدأ بـ MAH-
    balance = db.Column(db.Float, default=0.0)
    
    def generate_wallet(self):
        """توليد رقم محفظة فريد بصيغة MAH- و 8 رموز"""
        chars = string.ascii_uppercase + string.digits
        random_part = ''.join(random.choices(chars, k=8))
        self.wallet_id = f"MAH-{random_part}"

# استيراد الدالة في بداية app.py
from models import seed_system 

# ... كود تهيئة التطبيق (app = Flask...)

# المكان الصحيح للاستدعاء:
with app.app_context():
    db.create_all()  # ينشئ الجداول أولاً
    seed_system()    # يحقن البيانات (علي محجوب ومحجوب أونلاين) ثانياً
    print("✅ تم فحص قاعدة البيانات وتجهيز الحسابات السيادية.")

# ... بقية المسارات (Routes)
