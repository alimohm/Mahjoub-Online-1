from database import db
from datetime import datetime

class AdminUser(db.Model):
    __tablename__ = 'admin_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default="Super Admin")

class Vendor(db.Model):
    __tablename__ = 'vendor'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    brand_name = db.Column(db.String(150))
    employee_name = db.Column(db.String(150))
    phone_number = db.Column(db.String(20))
    status = db.Column(db.String(50), default="نشط")
    wallet_address = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    staff = db.relationship('VendorStaff', backref='owner', lazy=True)

class VendorStaff(db.Model):
    __tablename__ = 'vendor_staff'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    national_id = db.Column(db.String(100), nullable=False)

def seed_system():
    if not AdminUser.query.filter_by(username="علي محجوب").first():
        db.session.add(AdminUser(username="علي محجوب", password="admin_password_123", role="Super Admin"))
    if not Vendor.query.filter_by(username="ali_mahjoub").first():
        db.session.add(Vendor(username="ali_mahjoub", password="vendor_password_123", brand_name="محجوب أونلاين", status="نشط"))
    db.session.commit()
    print("✨ تم فحص وحقن البيانات السيادية بنجاح.")
