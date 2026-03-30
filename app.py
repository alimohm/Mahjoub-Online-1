import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'mahjoub_online_2026_key')

# --- إعدادات الربط مع قاعدة بيانات Railway ---
# سحب الرابط من المتغيرات
database_url = os.environ.get('DATABASE_URL')

# تصحيح الرابط ليتوافق مع SQLAlchemy 3.0+
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# تحسين استقرار الاتصال لمنع الانهيار
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}

db = SQLAlchemy(app)

# --- تعريف الجداول ---
class Vendor(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)
    brand_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

# --- محرك الإنشاء التلقائي ---
def init_db():
    with app.app_context():
        try:
            # محاولة إنشاء الجداول إذا لم تكن موجودة
            db.create_all()
            # إضافة حسابك (ali) تلقائياً لتتمكن من الدخول فوراً
            if not Vendor.query.filter_by(username='ali').first():
                admin = Vendor(
                    username='ali',
                    password='123',
                    owner_name='علي محجوب',
                    brand_name='محجوب أونلاين',
                    phone_number='777777777',
                    email='admin@mahjoub.online'
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ تم تجهيز القاعدة وإضافة حسابك بنجاح!")
        except Exception as e:
            print(f"❌ خطأ أثناء تهيئة القاعدة: {e}")

# تنفيذ التهيئة عند بدء التشغيل
init_db()

# --- المسارات البرمجية ---
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        vendor = Vendor.query.filter_by(username=u).first()
        if vendor and vendor.password == p:
            session.update({
                'vendor_id': vendor.id,
                'vendor_name': vendor.owner_name,
                'brand_name': vendor.brand_name
            })
            return redirect(url_for('dashboard'))
        flash("خطأ في اسم المستخدم أو كلمة المرور", "danger")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    return f"مرحباً {session['vendor_name']} في لوحة تحكم {session['brand_name']}"

if __name__ == "__main__":
    # استخدام المنفذ الذي يحدده Railway
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
