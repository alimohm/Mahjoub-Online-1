from flask_sqlalchemy import SQLAlchemy

# تعريف المحرك مرة واحدة فقط
db = SQLAlchemy()

def init_db(app):
    """ربط قاعدة البيانات بالتطبيق"""
    db.init_app(app)
