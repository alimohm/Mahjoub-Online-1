from flask import Flask
from database import init_db
from config import Config

app = Flask(__name__)
# تحميل الإعدادات لإنهاء خطأ SQLALCHEMY_DATABASE_URI
app.config.from_object(Config)

init_db(app)

# ... باقي المسارات (login_view, etc.)
