import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# --- الاستدعاءات الجوهرية للملفات الأخرى ---
from database import db, init_db, Vendor, Product
from config import Config
import finance         # استدعاء ملف الحسبة المالية (30%)
import bridge_logic    # استدعاء ملف الويب هوك (الربط بالمتجر)

app = Flask(__name__)
app.config.from_object(Config)

# إعداد مجلد الصور
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# تهيئة قاعدة البيانات
init_db(app)

# --- 1. مسار تسجيل الدخول (Login) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Vendor.query.filter_by(username=request.form.get('username')).first()
        # تحقق بسيط من كلمة المرور (يفضل استخدام التشفير لاحقاً)
        if user and user.password == request.form.get('password'):
            session['vendor_id'] = user.id
            return redirect(url_for('dashboard'))
        flash("خطأ في اسم المستخدم أو كلمة المرور")
    return render_template('login.html')

# --- 2. مسار لوحة التحكم (Dashboard) ---
@app.route('/')
@app.route('/dashboard')
def dashboard():
    v_id = session.get('vendor_id')
    if not v_id:
        return redirect(url_for('login'))
    
    vendor = Vendor.query.get(v_id)
    # جلب منتجات هذا المورد فقط لعرضها في الهيكل
    vendor_products = Product.query.filter_by(vendor_id=v_id).all()
    return render_template('dashboard.html', vendor=vendor, products=vendor_products)

# --- 3. مسار إضافة المنتج (Action) ---
@app.route('/add_product', methods=['POST'])
def add_product():
    v_id = session.get('vendor_id')
    if not v_id: return redirect(url_for('login'))
    
    vendor = Vendor.query.get(v_id)
    file = request.files.get('image')
    
    # أ- معالجة الصورة
    image_url = ""
    if file and file.filename != '':
        filename = secure_filename(f"qmr_{v_id}_{file.filename}")
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        # استخدام رابط ريلوي الديناميكي
        image_url = f"{request.url_root.rstrip('/')}/static/uploads/{filename}"

    # ب- الحسبة المالية عبر ملف finance.py
    raw_p = request.form.get('price')
    curr = request.form.get('currency')
    f_price = finance.calculate_final_price(raw_p, curr)

    # ج- الحفظ في قاعدة البيانات المحلية (قمرة كلاود)
    new_p = Product(
        name=request.form.get('name'),
        description=request.form.get('description'),
        cost_price=float(raw_p),
        final_price=f_price,
        image_url=image_url,
        vendor_id=v_id
    )
    db.session.add(new_p)
    db.session.commit()

    # د- الإرسال للمتجر عبر bridge_logic.py
    data = {
        "name": new_p.name,
        "final_price": f_price,
        "description": new_p.description,
        "image_url": image_url,
        "wallet": vendor.wallet_address
    }
    
    if bridge_logic.push_to_store(data):
        flash(f"تم بنجاح! السعر النهائي في المتجر: {f_price} ر.س")
    else:
        flash("تم الحفظ في قمرة، لكن فشل إرسال الويب هوك للمتجر.")
        
    return redirect(url_for('dashboard'))

# --- 4. تسجيل الخروج ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    # التأكد من إنشاء الجداول قبل التشغيل
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
