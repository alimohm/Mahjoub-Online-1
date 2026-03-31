from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    owner_name = db.Column(db.String(120))
    brand_name = db.Column(db.String(120))
    wallet_address = db.Column(db.String(200))
    products = db.relationship('Product', backref='vendor', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    cost_price = db.Column(db.Float, nullable=False)
    final_price = db.Column(db.Float)
    image_url = db.Column(db.String(255))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)

def init_db(app):
    db.init_app(app)
