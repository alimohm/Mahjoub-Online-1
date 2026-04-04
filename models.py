from database import db
from datetime import datetime
import string
import random

# --- [ 1. جدول الإدارة العليا: علي محجوب ] ---
class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False) # باللغة العربية
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default="Super Admin")

# --- [ 2. جدول الموردين (المالك الأصلي) ] ---
class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    brand_name = db.Column(db.String(150), nullable=False)
    doc_type = db.Column(db.String(50)) # (سجل تجاري، مزاولة مهنة، هوية وطنية)
    address_text = db.Column(db.String(255))
    location_url = db.Column(db.String(500))
    status = db.Column(db.String(50), default="منشط")
    
    # العلاقات
    staff = db.relationship('VendorStaff', backref='owner', lazy=True)
    products = db.relationship('Product', backref='vendor', lazy=True)

# --- [ 3. جدول موظفي المورد ] ---
class VendorStaff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    national_id = db.Column(db.String(100), nullable=False) # الهوية الرسمية للموظف

# --- [ 4. جدول المنتجات والمحفظة ] ---
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    wallet_id = db.Column(db.String(20), unique=True) # MAH-XXXXXXXX

# --- [ دالة حقن البيانات السيادية ] ---
def seed_system():
    # حقن علي محجوب (المالك العام)
    if not AdminUser.query.filter_by(username="علي محجوب").first():
        db.session.add(AdminUser(username="علي محجوب", password="admin_password_123"))
    
    # حقن مورد تجريبي (محجوب أونلاين)
    if not Vendor.query.filter_by(username="محجوب أونلاين").first():
        v = Vendor(
            username="محجوب أونلاين", 
            password="vendor_pass_123", 
            brand_name="محجوب أونلاين للخدمات الرقمية", 
            status="منشط"
        )
        db.session.add(v)
        db.session.commit() # للحصول على الـ ID لربط الموظف
        
        # حقن موظف تابع للمورد
        db.session.add(VendorStaff(
            vendor_id=v.id, 
            username="موظف تجريبي", 
            password="staff_pass_123", 
            national_id="10203040"
        ))
    
    db.session.commit()
    print("✨ تم فحص وحقن البيانات السيادية بنجاح.")
