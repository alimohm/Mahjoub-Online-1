import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# 1. استيراد الإعدادات والتهيئة
from config import Config
from database import db, init_db

# 2. استيراد الجداول من models.py (المكان الجديد والآمن)
from models import Product, Vendor

# 3. استيراد منطق العمل (تسجيل الدخول والتحقق)
from logic import login_vendor, logout, is_logged_in

# 4. استيراد خدمة المزامنة مع قمرة
from sync_service import send_to_qumra_webhook

app = Flask(__name__)
app.config.from_object(Config)

# إعدادات المجلدات والرفع (للملفات المؤقتة قبل المزامنة)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# تهيئة قاعدة البيانات (PostgreSQL في Railway)
init_db(app)

# --- المسارات (Routes) ---

# 1. الصفحة الرئيسية (توجيه ذكي)
@app.route('/')
def index():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

# 2. بوابة تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')
        
        if login_vendor(user, pw):
            return redirect(url_for('dashboard'))
        # تنبيه الخطأ يأتي من دالة login_vendor داخل logic.py
    
    return render_template('login.html')

# 3. لوحة التحكم (الداشبورد) - مع ميزة الفلترة (الاختفاء)
@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    user_session = session.get('username')
    
    # جلب المنتجات التي لم تُنشر بعد فقط (is_published=False) لكي تختفي بعد المزامنة
    try:
        vendor = Vendor.query.filter_by(username=user_session).first()
        products = Product.query.filter_by(vendor_username=user_session, is_published=False).all()
        products_count = len(products)
    except Exception as e:
        print(f"⚠️ خطأ في قاعدة البيانات: {e}")
        products = []
        products_count = 0

    return render_template('dashboard.html', 
                           vendor=vendor, 
                           products=products, 
                           products_count=products_count)

# 4. إضافة منتج جديد (الربط مع قمرة)
@app.route('/add_product', methods=['POST'])
def add_product():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    p_name = request.form.get('name')
    p_price = request.form.get('price')
    p_desc = request.form.get('description', '')
    p_image = request.files.get('image')

    if p_name and p_price:
        try:
            # معالجة الصورة
            image_filename = None
            if p_image and p_image.filename != '':
                ext = os.path.splitext(p_image.filename)[1]
                image_filename = f"{secure_filename(p_name)}_{os.urandom(2).hex()}{ext}"
                p_image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

            # حفظ المنتج محلياً في PostgreSQL
            new_item = Product(
                name=p_name,
                price=float(p_price),
                description=p_desc,
                image_file=image_filename,
                vendor_username=session['username']
            )
            db.session.add(new_item)
            db.session.commit()

            # --- البدء في عملية المزامنة مع قمرة ---
            # نرسل البيانات لـ GraphQL
            success = send_to_qumra_webhook(p_name, p_price, p_desc, image_filename)
            
            if success:
                # إذا نجحت المزامنة، نجعل المنتج "مخفياً" من لوحة المورد
                new_item.is_published = True
                db.session.commit()
                flash(f"✅ تم رفع {p_name} بنجاح إلى متجر قمرة!", "success")
            else:
                flash(f"⚠️ تم حفظ المنتج محلياً، لكن فشل إرساله لقمرة. سيبقى ظاهراً للمراجعة.", "warning")

        except Exception as e:
            db.session.rollback()
            flash(f"❌ خطأ فني: {str(e)}", "danger")

    return redirect(url_for('dashboard'))

# 5. تسجيل الخروج
@app.route('/logout')
def logout_route():
    return logout() # يستدعي الدالة من logic.py

if __name__ == '__main__':
    # وضع التصحيح مفعل لكشف أي أخطاء في Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
