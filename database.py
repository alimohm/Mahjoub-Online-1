import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    # تحويل الرابط ليتوافق مع مكتبة SQLAlchemy الحديثة
    uri = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
    if uri.startswith("postgres://"): uri = uri.replace("postgres://", "postgresql://", 1)
    
    app.config.update(
        SQLALCHEMY_DATABASE_URI=uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY=os.environ.get('SK', 'M_26_R')
    )
    db.init_app(app)
    with app.app_context(): db.create_all()

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    owner_name = db.Column(db.String(120))
