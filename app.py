import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# --- استدعاء المنطق المنفصل ---
try:
    from database import db, init_db, Vendor, Product
    from config import Config
    import finance        # لحساب زيادة الـ 30%
    import bridge_logic   # لربط المحفظة والويب هوك
except ImportError as e:
    print(f"خطأ في الملفات المنفصلة: {e}")

app = Flask(__name__)
app.config.from_object(Config)

# تهيئة القاعدة ومجلد الصور
init_db(app)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# إنشاء الجداول والمستخدم فور التشغيل لمنع خطأ 500
with app.app_context():
    db.create_all()
    if not Vendor.query.filter_by(username="ali").first():
        # إضافة مستخدم بصلاحيات كاملة ومحفظة افتراضية
        v = Vendor(username="ali", password="123", owner_name="Ali Mahjoub", wallet_address="MQ-2026-X")
        db.session.add(v)
        db.session.commit()

# --- المسارات البرمجية ---

@app.route('/')
def home():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # واجهة الدخول الملكية
    if request.method == 'POST':
        user = Vendor.query.filter_by(username=request.form.get('username')).first()
        if user and user.password == request.form.get('password'):
            session['vendor_id'] = user.id
            return redirect(url_for('dashboard'))
        flash("بيانات الدخول غير صحيحة")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """هذا هو الهيكل الداخلي الذي تطلبه"""
    v_id = session.get('vendor_id')
    if not v_id: return redirect(url_for('login'))
    
    vendor = Vendor.query.get(v_id)
    # نمرر الـ vendor لكي تظهر المحفظة والمنتجات
    return render_template('dashboard.html', vendor=vendor)

@app.route('/add_product', methods=['POST'])
def add_product():
    """منطق رفع المنتج وحساب السعر"""
    v_id = session.get('vendor_id')
    if not v_id: return redirect(url_for('login'))
    
    vendor = Vendor.query.get(v_id)
    file = request.files.get('image')
    cost = request.form.get('price')

    # 1. الحسبة المالية من ملف finance.py المنفصل
    final_price = finance.calculate_final_price(cost, "USD")

    # 2. معالجة صورة المنتج
    img_path = ""
    if file:
        filename = secure_filename(f"v_{v_id}_{file.filename}")
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        img_path = f"/static/uploads/{filename}"

    # 3. الحفظ في قاعدة البيانات عبر database.py
    new_p = Product(name=request.form.get('name'), cost_price=float(cost), 
                    final_price=final_price, image_url=img_path, vendor_id=v_id)
    db.session.add(new_p)
    db.session.commit()

    # 4. إرسال البيانات للمتجر عبر bridge_logic.py
    bridge_logic.push_to_store({
        "name": new_p.name, 
        "price": final_price, 
        "wallet": vendor.wallet_address
    })
    
    flash("تم رفع المنتج وتحديث المحفظة!")
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
