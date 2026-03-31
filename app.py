import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'mahjoub_2026_key')

# --- إعداد قاعدة البيانات ---
# تأكد أن DATABASE_URL في ريلوي هو الرابط العام (Public URL)
db_url = os.environ.get('DATABASE_URL')

if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- النماذج البرمجية (مطابقة لصورة قاعدة بياناتك) ---
class Vendor(db.Model):
    __tablename__ = 'vendor' # اسم الجدول بالمفرد
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    owner_name = db.Column(db.String(100)) # مطابق لـ owner_name في صورتك
    wallet_address = db.Column(db.String(100)) # مطابق لـ wallet_address في صورتك

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))

# --- المسارات ---

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        
        # البحث عن المورد (مثل 'ali' و '123' في صورتك)
        vendor = Vendor.query.filter_by(username=u, password=p).first()
        
        if vendor:
            session['vendor_id'] = vendor.id
            return redirect(url_for('dashboard'))
        else:
            flash("بيانات الدخول غير صحيحة")
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # جلب بيانات المورد صاحب الـ ID الموجود في الجلسة
        vendor_data = Vendor.query.get(session['vendor_id'])
        
        if not vendor_data:
            session.clear()
            return redirect(url_for('login'))
            
        # جلب المنتجات (إن وجدت)
        products_list = Product.query.filter_by(vendor_id=vendor_data.id).all()
        
        # عرض القالب مع تمرير البيانات الصحيحة
        return render_template('dashboard.html', vendor=vendor_data, products=products_list)
        
    except Exception as e:
        # سيظهر هذا النص في حالة وجود مشكلة في DATABASE_URL
        return f"خطأ في الاتصال بقاعدة البيانات: {str(e)}", 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    # التشغيل على منفذ ريلوي الافتراضي
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
