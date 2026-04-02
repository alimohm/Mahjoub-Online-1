import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# استيراد إعداداتك الخاصة (تأكد من وجود هذه الملفات في مجلد المشروع)
from config import Config
from database import db, init_db, Product, Vendor 
from logic import login_vendor, logout, is_logged_in
from sync_service import send_to_qumra_webhook 

app = Flask(__name__)
app.config.from_object(Config)

# 1. إعداد مسار الرفع (الحل الجذري لمنع انهيار الـ API)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # حد أقصى 16 ميجا للرفع
os.makedirs(UPLOAD_FOLDER, exist_ok=True) 

# تهيئة قاعدة البيانات
init_db(app)

@app.route('/')
def index():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')
        if login_vendor(user, pw):
            return redirect(url_for('dashboard'))
        flash("❌ خطأ في اسم المستخدم أو كلمة المرور", "danger")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    vendor = Vendor.query.filter_by(username=session['username']).first()
    try:
        products = Product.query.filter_by(vendor_username=session['username']).all()
        products_count = len(products)
    except Exception as e:
        print(f"⚠️ تنبيه: {e}")
        products_count = 0
        products = []
    
    return render_template('dashboard.html', vendor=vendor, products_count=products_count, products=products)

@app.route('/add_product', methods=['POST']) # جعلناه POST فقط لخدمة النافذة المنبثقة
def add_product():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    try:
        # استقبال البيانات من النافذة (Modal)
        p_name = request.form.get('p_name')
        p_price = request.form.get('p_price')
        p_currency = request.form.get('p_currency', 'MAH')
        p_desc = request.form.get('p_desc', '') 
        
        if not p_name or not p_price:
            flash("❌ بيانات المنتج ناقصة", "danger")
            return redirect(url_for('dashboard'))

        # معالجة الصور والفيديو
        p_images = request.files.getlist('p_images')
        main_image = None
        safe_name = secure_filename(p_name).replace(' ', '_')

        for i, img in enumerate(p_images):
            if img and img.filename != '':
                ext = os.path.splitext(img.filename)[1]
                filename = f"{safe_name}_{i+1}{ext}"
                img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                if i == 0: main_image = filename

        # حفظ في قاعدة البيانات
        full_desc = f"[{p_currency}] {p_desc}"
        new_item = Product(
            name=p_name,
            price=float(p_price),
            description=full_desc,
            image_file=main_image, 
            vendor_username=session['username']
        )
        db.session.add(new_item)
        db.session.commit()
        
        # المزامنة مع قمرة (API خارجي)
        try:
            send_to_qumra_webhook(p_name, f"{p_price} {p_currency}", p_desc, main_image)
            flash(f"🚀 تم رفع {p_name} بنجاح!", "success")
        except:
            flash("✅ تم الحفظ محلياً، فشلت المزامنة الخارجية مؤقتاً", "warning")

    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {e}")
        flash("❌ حدث خطأ أثناء المعالجة", "danger")

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout_route():
    return logout()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
