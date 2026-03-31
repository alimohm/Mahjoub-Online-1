import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# --- استدعاء الملفات الجانبية (نظام المنطق المنفصل) ---
# التأكد من استدعاء الوظائف من الملفات التي تظهر في المجلد الخاص بك
try:
    from database import db, init_db, Vendor, Product
    from config import Config
    import finance  # الملف المسؤول عن حسابات السعر والـ 30%
    import bridge_logic  # الملف المسؤول عن إرسال البيانات للمتجر (Webhook)
except ImportError as e:
    print(f"خطأ في استدعاء الملفات المنطقية: {e}")

app = Flask(__name__)
app.config.from_object(Config)

# تهيئة قاعدة البيانات (Postgres) ومجلد الصور
init_db(app)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# إنشاء الجداول والمستخدم عند بدء التشغيل لمنع خطأ 500
with app.app_context():
    db.create_all() 
    # التأكد من وجود حساب المالك (علي محجوب)
    if not Vendor.query.filter_by(username="ali").first():
        test_v = Vendor(username="ali", password="123", owner_name="Ali Mahjoub")
        db.session.add(test_v)
        db.session.commit()

# --- المسارات (Routes) ---

@app.route('/')
def home():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Vendor.query.filter_by(username=request.form.get('username')).first()
        if user and user.password == request.form.get('password'):
            session['vendor_id'] = user.id
            return redirect(url_for('dashboard'))
        flash("خطأ في بيانات الدخول الملكية")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """عرض الهيكل الداخلي للوحة التحكم"""
    v_id = session.get('vendor_id')
    if not v_id: return redirect(url_for('login'))
    vendor = Vendor.query.get(v_id)
    return render_template('dashboard.html', vendor=vendor)

@app.route('/add_product', methods=['POST'])
def add_product():
    v_id = session.get('vendor_id')
    if not v_id: return redirect(url_for('login'))
    
    vendor = Vendor.query.get(v_id)
    file = request.files.get('image')
    
    # 1. معالجة الصورة
    image_url = ""
    if file:
        filename = secure_filename(f"{v_id}_{file.filename}")
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        image_url = f"{request.url_root.rstrip('/')}/static/uploads/{filename}"

    # 2. استدعاء منطق الحسبة المالية من ملف finance.py المنفصل
    try:
        price_input = request.form.get('price')
        f_price = finance.calculate_final_price(price_input, "USD")

        # 3. الحفظ في قاعدة البيانات عبر ملف database.py المنفصل
        new_p = Product(
            name=request.form.get('name'),
            cost_price=float(price_input),
            final_price=f_price,
            image_url=image_url,
            vendor_id=v_id
        )
        db.session.add(new_p)
        db.session.commit()

        # 4. إرسال البيانات للمتجر عبر ملف bridge_logic.py المنفصل
        bridge_logic.push_to_store({
            "name": new_p.name, 
            "final_price": f_price, 
            "image_url": image_url, 
            "wallet": vendor.wallet_address
        })
        
        flash("تم النشر بنجاح في المنصة!")
    except Exception as e:
        flash(f"حدث خطأ في المنطق: {e}")

    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    # التشغيل المتوافق مع بورت Railway
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
