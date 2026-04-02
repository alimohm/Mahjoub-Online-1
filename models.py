from database import db
import random
import string

def generate_mah_wallet():
    """توليد محفظة تبدأ بـ MAH متبوعة بـ 10 رموز عشوائية"""
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"MAH-{suffix}"

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    wallet_address = db.Column(db.String(255), unique=True)
    brand_name = db.Column(db.String(120))
    # حقل إضافي لمفتاح ربط قمرة
    qomra_api_key = db.Column(db.Text, nullable=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500)) 
    image_file = db.Column(db.String(200))
    description = db.Column(db.Text)
    is_published = db.Column(db.Boolean, default=False) # الحقل المسؤول عن الاختفاء
    qomra_id = db.Column(db.String(100))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    vendor_username = db.Column(db.String(80))
