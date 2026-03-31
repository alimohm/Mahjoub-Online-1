import os, random, string
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def generate_wallet():
    # توليد محفظة فريدة تبدأ بـ MQ
    return "MQ-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def init_db(app):
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url or 'sqlite:///qamrah_cloud.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    owner_name = db.Column(db.String(100))
    wallet_address = db.Column(db.String(20), default=generate_wallet, unique=True)
    products = db.relationship('Product', backref='owner', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    cost_price = db.Column(db.Float, nullable=False)
    final_price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500))
    currency = db.Column(db.String(10), default='SAR')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
