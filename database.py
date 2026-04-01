import random, string
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    wallet_address = db.Column(db.String(255), unique=True) # محفظة MQ
    brand_name = db.Column(db.String(120))

def generate_mq_wallet():
    """توليد عنوان محفظة MQ الفريد"""
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"MQ-{suffix}"

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all() # إنشاء الجداول السيادية
