import os
import random
import string
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def generate_wallet():
    # توليد محفظة فريدة تبدأ بـ MQ
    return "MQ-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def init_db(app):
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///qamrah.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

# 1. جدول الموردين
class Vendor(db.Model):
    __tablename__ = 'vendor'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    owner_name = db.Column(db.String(100))
    wallet_address = db.Column(db.String(20), default=generate_wallet, unique=True)
    
    # علاقة تربط المورد بمنتجاته
    products = db.relationship('Product', backref='owner', lazy=True)

# 2. جدول المنتجات المستقل
class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    cost_price = db.Column(db.Float, nullable=False)    # السعر الأصلي الذي أدخله المورد
    sale_price = db.Column(db.Float, nullable=False)    # السعر بعد إضافة 30%
    currency = db.Column(db.String(10), default='SAR') # العملة المختارة
    status = db.Column(db.String(20), default='draft')  # حالة المنتج (مسودة/منشور)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # الربط مع المورد (Foreign Key)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
