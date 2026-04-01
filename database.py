from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def init_db(app):
    # تحميل الإعدادات من ملف config
    app.config.from_object(Config)
    db.init_app(app)
    
    with app.app_context():
        # إنشاء الجداول إذا لم تكن موجودة لضمان استقرار البيئة
        db.create_all()

# نموذج المورد (Vendor) الأساسي
class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    owner_name = db.Column(db.String(120))
    wallet_balance = db.Column(db.Float, default=0.0)
