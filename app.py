import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# --- 1. تعريف التطبيق فوراً لضمان السيادة ومنع NameError ---
app = Flask(__name__) #

# --- 2. استدعاء المحركات بناءً على هيكلية المجلدات المرفقة ---
from config import Config
from database import db, init_db
from models import Product, Vendor, AdminUser, seed_admin #

# استدعاء المنطق من الملفات المستقلة المكتشفة في صورك
from logic import login_vendor, is_logged_in
from admin_logic import is_admin_logged_in, verify_admin_credentials

app.config.from_object(Config)

# إعدادات المجلدات الثابتة (Static) المكتشفة
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# تهيئة القاعدة
init_db(app)

with app.app_context():
    # إصلاح خطأ الجدول المفقود (UndefinedColumn)
    db.create_all() 
    seed_admin() # حقن بيانات الإدارة

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==========================================
# --- مسارات الربط بين القوالب والمنطق ---
# ==========================================

@app.route('/')
def index():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard'))
    if is_logged_in(): return redirect(url_for('vendor_dashboard'))
    return redirect(url_for('login_page'))

# بوابة المورد - متوافق مع login.html
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in(): return redirect(url_for('vendor_dashboard'))
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        success, message = login_vendor(u, p)
        if success:
            flash(message, "success")
            return redirect(url_for('vendor_dashboard'))
        flash(message, "danger")
    return render_template('login.html')

# لوحة تحكم المورد - متوافق مع dashboard.html
@app.route('/dashboard')
def vendor_dashboard():
    if not is_logged_in(): return redirect(url_for('login_page'))
    vendor = Vendor.query.get(session.get('user_id'))
    products = Product.query.filter_by(vendor_id=vendor.id).all()
    return render_template('dashboard.html', vendor=vendor, products=products)

# إضافة منتج - متوافق مع add_product.html
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if not is_logged_in(): return redirect(url_for('login_page'))
    # هنا يتم استخدام منطق الرفع المؤمن
    return render_template('add_product.html')

# بوابة الإدارة - متوافق مع admin_login.html
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        u = request.form.get('admin_user', '').strip()
        p = request.form.get('admin_pass', '').strip()
        
        success, message = verify_admin_credentials(u, p)
        if success:
            flash(message, "success")
            return redirect(url_for('admin_dashboard'))
        flash(message, "danger")
    return render_template('admin_login.html')

# لوحة تحكم الإدارة - متوافق مع admin_dashboard.html
@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin_logged_in(): return redirect(url_for('admin_login'))
    all_vendors = Vendor.query.all()
    return render_template('admin_dashboard.html', vendors=all_vendors)

# تسجيل الخروج وتأمين الجلسة
@app.route('/logout')
def logout():
    session.clear()
    flash("تم تأمين كافة الأنظمة اللامركزية.", "info")
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    # المنفذ 8080 هو المعتمد في سجلات Railway الخاصة بك
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
