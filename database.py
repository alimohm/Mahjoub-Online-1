import os
import random
import string
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    owner_name = db.Column(db.String(120))
    brand_name = db.Column(db.String(120))
    brand_logo_url = db.Column(db.String(255))
    wallet_address = db.Column(db.String(255), unique=True)

def generate_mah_wallet():
    """توليد محفظة MAH السيادية"""
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(random.choice(chars) for _ in range(8))
    return f"MAH-{suffix}"

def init_db(app):
    uri = os.environ.get('DATABASE_URL')
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    app.config.update(
        SQLALCHEMY_DATABASE_URI=uri or 'sqlite:///local.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY=os.environ.get('SK', 'MAHJOUB_2026')
    )
    db.init_app(app)
    
    with app.app_context():
        try:
            db.create_all() # بناء الجداول إذا لم تكن موجودة
            if not Vendor.query.filter_by(username='ali').first():
                new_v = Vendor(
                    username='ali', password='123',
                    owner_name='علي محجوب', brand_name='محجوب أونلاين',
                    wallet_address=generate_mah_wallet()
                )
                db.session.add(new_v)
                db.session.commit()
        except Exception as e:
            print(f"Database Error: {e}")
