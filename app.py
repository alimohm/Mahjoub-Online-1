import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# --- 1. استيراد الإعدادات والمنطق ---
from config import Config
from database import db, init_db
from models import Product, Vendor, AdminUser, seed_admin
from logic import login_vendor, is_logged_in
from admin_logic import is_admin_logged_in, verify_admin_credentials, logout_admin_logic

app = Flask(__name__)
app.config.from_object(Config)

# إعدادات الرفع (الميديا)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # حد أقصى 16 ميجا
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- 2. تفعيل قاعدة البيانات وحقن الهوية ---
init_db(app)
with app.app_context():
    db.create_all()
    seed_admin() 

# ==========================================
# --- 3. مسار المورد (Dashboard) ---
# ==========================================
@app.route('/dashboard')
def dashboard():
    if not is_logged_in(): 
        return redirect(url_for('login_page'))
    
    vendor_data = Vendor.query.filter_by(username=session.get('username')).first()
    
    if not vendor_data:
        flash("فشلت عملية التحقق من الهوية اللامركزية.", "danger")
        session.clear()
        return redirect(url_for('login_page'))
        
    products_list = Product.query.filter_by(brand=vendor_data.brand_name).all()
    
    return render_template('dashboard.html', vendor=vendor_data, products=products_list)

# ==========================================
# --- 4. مسار رفع المنتجات (الذكاء الاصطناعي والميديا) ---
# ==========================================
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if not is_logged_in(): 
        return redirect(url_for('login_page'))
    
    vendor_data = Vendor.query.filter_by(username=session.get('username')).first()

    if request.method == 'POST':
        # سحب البيانات من فورم التصميم الاحترافي
        name = request.form.get('name')
        price = request.form.get('price')
        currency = request.form.get('currency')
        stock = request.form.get('stock')
        description = request.form.get('description')
        brand = request.form.get('brand')

        # معالجة رفع ألبوم الميديا (صور وفيديو)
        files = request.files.getlist('product_media')
        saved_files = []
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # إضافة اسم المورد لضمان عدم تكرار الأسماء
                unique_name = f"{vendor_data.username}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_name))
                saved_files.append(unique_name)

        # إنشاء كائن المنتج الجديد
        new_product = Product(
            name=name,
            price=float(price),
            description=description,
            brand=brand,
            image_url=",".join(saved_files) if saved_files else "default.jpg",
            status='pending' # المراجعة في برج المراقبة
        )
        
        # ملاحظة: إذا أضفت حقول currency و stock في الـ Models، قم بتفعيلها هنا:
        # new_product.currency = currency
        # new_product.stock = int(stock)

        db.session.add(new_product)
        db.session.commit()

        flash(f"🚀 تم رفع '{name}' بنجاح! سيظهر في المتجر بعد مراجعة الإدارة.", "success")
        return redirect(url_for('dashboard'))

    return render_template('add_product.html', vendor=vendor_data)

# ==========================================
# --- 5. مسار الإدارة (برج المراقبة) ---
# ==========================================
@app.route('/admin/dashboard')
def admin_dashboard_route():
    if not is_admin_logged_in(): 
        return redirect(url_for('admin_login_route'))
    
    all_vendors = Vendor.query.all()
    pending_items = Product.query.filter_by(status='pending').all()
    
    return render_template('admin_dashboard.html', 
                           vendors=all_vendors, 
                           pending_count=len(pending_items),
                           pending_items=pending_items)

# ==========================================
# --- 6. بقية المسارات والتشغيل ---
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in(): return redirect(url_for('dashboard'))
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        if login_vendor(u, p):
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login_route():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard_route'))
    if request.method == 'POST':
        u = request.form.get('admin_user')
        p = request.form.get('admin_pass')
        if verify_admin_credentials(u, p):
            return redirect(url_for('admin_dashboard_route'))
    return render_template('admin_login.html')

@app.route('/')
def home_redirect():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard_route'))
    if is_logged_in(): return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/logout')
def logout_route():
    session.clear()
    flash("تم تأمين الجلسة والخروج بنجاح.", "info")
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
