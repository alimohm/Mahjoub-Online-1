import random
import string
from database import db

def generate_mah_wallet():
    """توليد عنوان محفظة فريد يبدأ بـ MAH متبوع بـ 10 رموز"""
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"MAH-{suffix}"

class Vendor(db.Model):
    __tablename__ = 'vendor'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    brand_name = db.Column(db.String(120))
    
    # المحفظة الرقمية الخاصة بـ "محجوب أونلاين"
    wallet_address = db.Column(db.String(255), unique=True, default=generate_mah_wallet)
    
    # توكن الربط مع متجر قمرة (اختياري إذا كان لكل مورد توكن خاص)
    qomra_access_token = db.Column(db.Text, nullable=True)
    
    # علاقة مع المنتجات
    products = db.relationship('Product', backref='vendor_owner', lazy=True)

class Product(db.Model):
    __tablename__ = 'product'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    
    # مسار الصورة المرفوعة محلياً على السيرفر
    image_file = db.Column(db.String(200))
    
    # رابط خارجي (في حال الحاجة مستقبلاً)
    image_url = db.Column(db.String(500))
    
    # --- منطق المزامنة والاختفاء ---
    # القيمة الافتراضية False (يظهر في اللوحة)
    # بمجرد نجاح send_to_qumra_webhook تتحول لـ True (فيختفي من اللوحة)
    is_published = db.Column(db.Boolean, default=False)
    
    # معرف المنتج العائد من قاعدة بيانات قمرة (لفك اللغز لاحقاً)
    qomra_id = db.Column(db.String(100))
    
    # الربط مع المورد
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    vendor_username = db.Column(db.String(80))

    def __repr__(self):
        return f'<Product {self.name}>'
