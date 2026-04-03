import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# --- استيراد الملفات الخاصة بالمشروع ---
from config import Config
from database import db, init_db
from models import Product, Vendor
from logic import login_vendor, logout, is_logged_in
from admin_logic import is_admin_logged_in, verify_admin_credentials # نقلناها للأعلى

app = Flask(__name__)
app.config.from_object(Config)

# إعدادات الميديا
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

init_db(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- مسارات الموردين (Vendors) ---

@app.route('/')
def index():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in(): return redirect(url_for('dashboard'))
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        if login_vendor(u, p):
            flash("مرحباً بك في نظام محجوب أونلاين الإداري", "success")
            return redirect(url_for('dashboard'))
        flash("خطأ في بيانات الدخول.", "danger")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not is_logged_in(): return redirect(url_for('login_page'))
    user_session = session.get('username')
    vendor_data = Vendor.query.filter_by(username=user_session).first()
    if not vendor_data: return redirect(url_for('logout_route'))
    products_list = Product.query.filter_by(brand=vendor_data.brand_name).all()
    return render_template('dashboard.html', vendor=vendor_data, products=products_list)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if not is_logged_in(): return redirect(url_for('login_page'))
    user_session = session.get('username')
    vendor = Vendor.query.filter_by(username=user_session).first()

    if request.method == 'POST':
        p_name = request.form.get('name')
        p_price = request.form.get('price')
        p_currency = request.form.get('currency', 'YER')
        p_stock = request.form.get('stock', 1)
        p_desc = request.form.get('description')
        
        media_files = request.files.getlist('product_media')
        saved_files = []

        if p_name and p_price:
            for file in media_files:
                if file and allowed_file(file.filename):
                    ext = os.path.splitext(file.filename)[1]
                    filename = f"{secure_filename(p_name)}_{os.urandom(2).hex()}{ext}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    saved_files.append(filename)

            all_media_str = ",".join(saved_files) if saved_files else None

            new_item = Product(
                name=p_name,
                brand=vendor.brand_name,
                price=float(p_price),
                currency=p_currency,
                stock=int(p_stock),
                description=p_desc,
                image_file=all_media_str,
                vendor_id=vendor.id,
                vendor_username=user_session,
                status='pending' # لكي تظهر في لوحة الإدارة للموافقة
            )
            db.session.add(new_item)
            db.session.commit()
            flash(f"✅ تم إضافة المنتج وبانتظار موافقة الإدارة", "success")
            return redirect(url_for('dashboard'))

    return render_template('add_product.html', vendor=vendor)

# --- مسارات الإدارة (Admin) ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login_route():
    if request.method == 'POST':
        u = request.form.get('admin_user')
        p = request.form.get('admin_pass')
        if verify_admin_credentials(u, p):
            session['is_admin'] = True
            flash("مرحباً بك في لوحة الإدارة المركزية", "success")
            return redirect(url_for('admin_dashboard_route'))
        flash("خطأ في بيانات الدخول الإدارية!", "danger")
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard_route():
    if not is_admin_logged_in():
        return redirect(url_for('admin_login_route'))
    
    all_vendors = Vendor.query.all()
    pending_count = Product.query.filter_by(status='pending').count()
    return render_template('admin_dashboard.html', vendors=all_vendors, pending_count=pending_count)

@app.route('/logout')
def logout_route():
    session.clear() # يمسح جلسة المورد والمدير معاً
    return redirect(url_for('login_page'))

# --- تشغيل السيرفر (يجب أن يكون في النهاية) ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
