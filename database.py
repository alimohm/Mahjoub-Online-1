import os, random, string
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def generate_wallet():
    return "MQ-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def init_db(app):
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///qamrah.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

class Vendor(db.Model):
    __tablename__ = 'vendor'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    owner_name = db.Column(db.String(100))
    wallet_address = db.Column(db.String(20), default=generate_wallet, unique=True)
    products = db.relationship('Product', backref='vendor', lazy=True)

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    cost_price = db.Column(db.Float, nullable=False)
    final_price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500)) # عمود الصورة الجديد
    currency = db.Column(db.String(10), default='SAR')
    status = db.Column(db.String(20), default='draft')
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
