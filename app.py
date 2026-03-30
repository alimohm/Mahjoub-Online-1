import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# إعداد المفتاح السري (Secret Key) للأمان والجلسات
app.secret_key = os.environ.get('SECRET_KEY', 'mahjoub_online_private_key_2026')

# --- إعدادات قاعدة البيانات الذكية ---
# سحب الرابط المرجعي من Railway (DATABASE_URL)
database_url = os.environ.get('DATABASE_URL')

# تصحيح تنسيق الرابط ليتوافق مع SQLAlchemy 
# (تحويل postgres:// إلى postgresql:// إذا لزم الأمر)
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# تعيين الرابط في إعدادات التطبيق
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# خيارات إضافية لاستقرار الاتصال في البيئات السحابية
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}

db = SQLAlchemy(app)

# --- نموذج جدول الموردين (Vendors Table) ---
class Vendor(db.Model):
    __tablename__ = 'vendors'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)   # اسم المالك
    brand_name = db.Column(db.String(100), nullable=False)   # اسم العلامة التجارية
    phone_number = db.Column(db.String(20), nullable=False)  # رقم الهاتف
    email = db.Column(db.String(120), unique=True, nullable=False) # البريد
    address = db.Column(db.String(255), nullable=True)       # العنوان
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# --- تهيئة الجداول وحساب المسؤول الرئيسي ---
with app.app_context():
    try:
        db.create_all()
        # إضافة حسابك (ali) تلقائياً إذا لم يكن موجوداً
        if not Vendor.query.filter_by(username='ali').first():
            admin = Vendor(
                username='ali',
                password='123', # كلمة المرور التجريبية
                owner_name='علي محجوب',
                brand_name='محجوب ستور',
                phone_number='777777777',
                email='admin@mahjoub.online'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ تم إنشاء الجداول وإضافة حساب المورد بنجاح!")
    except Exception as e:
        print(f"⚠️ فشل الاتصال بقاعدة البيانات: {e}")

# --- المسارات البرمجية (Routes) ---

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_in = request.form.get('username', '').strip()
        pass_in = request.form.get('password', '').strip()
        
        vendor = Vendor.query.filter_by(username=user_in).first()
        
        if not vendor:
            flash("عذراً، هذا المورد غير مسجل في المنصة.", "danger")
        elif vendor.password != pass_in:
            flash("كلمة المرور غير صحيحة، حاول مجدداً.", "warning")
        else:
            session['vendor_id'] = vendor.id
            session['vendor_name'] = vendor.owner_name
            session['brand_name'] = vendor.brand_name
            return redirect(url_for('dashboard'))
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    # الحصول على المنفذ من Railway أو استخدام 5000 افتراضياً
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
