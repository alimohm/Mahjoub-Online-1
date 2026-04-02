import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# استيراد الإعدادات والمنطق البرمجي الخاص بك
from config import Config
from database import db, init_db, Product, Vendor 
from logic import login_vendor, logout, is_logged_in
from sync_service import send_to_qumra_webhook 

app = Flask(__name__)
app.config.from_object(Config)

# إعدادات رفع الملفات
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True) 

# تهيئة قاعدة البيانات
init_db(app)

@app.route('/')
def index():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

# --- بوابة الدخول ---
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')
        if login_vendor(user, pw):
            # إعداد بيانات الجلسة (المحفظة الرقمية)
            session['wallet'] = "0xMAH_" + os.urandom(4).hex().upper() 
            return redirect(url_for('dashboard'))
        flash("❌ خطأ في اسم المستخدم أو كلمة المرور", "danger")
    
    return render_template('login.html')

# --- لوحة التحكم (الداشبورد) ---
@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    # جلب بيانات المورد الحالي والمنتجات
    vendor = Vendor.query.filter_by(username=session['username']).first()
    products = Product.query.filter_by(vendor_username=session['username']).all()
    products_count = len(products)
    
    return render_template('dashboard.html', 
                           vendor=vendor, 
                           products_count=products_count)

# --- إضافة المنتج (دعم الرابط المباشر والنافذة) ---
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    if request.method == 'POST':
        # استقبال البيانات (لاحظ الأسماء المتوافقة مع HTML الخاص بك)
        p_name = request.form.get('name')
        p_price = request.form.get('price')
        p_desc = request.form.get('description', '') 
        p_image = request.files.get('image')

        if not p_name or not p_price:
            flash("❌ يرجى إدخال البيانات الأساسية للمنتج.", "danger")
            return redirect(url_for('dashboard'))

        try:
            # معالجة وحفظ الصورة
            image_filename = None
            if p_image and p_image.filename != '':
                ext = os.path.splitext(p_image.filename)[1]
                image_filename = f"{secure_filename(p_name)}_{os.urandom(2).hex()}{ext}"
                p_image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

            # الحفظ في قاعدة البيانات
            new_product = Product(
                name=p_name,
                price=float(p_price),
                description=p_desc,
                image_file=image_filename,
                vendor_username=session['username']
            )
            db.session.add(new_product)
            db.session.commit()
            
            # المزامنة مع المنصة الخارجية
            send_to_qumra_webhook(p_name, p_price, p_desc, image_filename)
            flash(f"🚀 تم رفع {p_name} ومزامنته بنجاح!", "success")
            
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash("❌ حدث خطأ أثناء الحفظ.", "danger")
            return redirect(url_for('dashboard'))

    return render_template('add_product.html')

@app.route('/logout')
def logout_route():
    return logout()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
