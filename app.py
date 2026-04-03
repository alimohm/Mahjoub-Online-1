import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# --- استيراد الملفات الخاصة بالمشروع ---
from config import Config
from database import db, init_db
from models import Product, Vendor, AdminUser, seed_admin
from logic import login_vendor, logout, is_logged_in
from admin_logic import is_admin_logged_in, verify_admin_credentials, logout_admin_logic

# 1. تعريف التطبيق (أساسي جداً)
app = Flask(__name__)
app.config.from_object(Config)

# إعدادات الميديا
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 2. ربط قاعدة البيانات وتفعيل سياق التطبيق
init_db(app)

with app.app_context():
    db.create_all()
    seed_admin() # إنشاء حساب "صبري" إذا لم يكن موجوداً

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==========================================
# --- مسارات الموردين (Vendors) ---
# ==========================================

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
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not is_logged_in(): return redirect(url_for('login_page'))
    user_session = session.get('username')
    vendor_data = Vendor.query.filter_by(username=user_session).first()
    if not vendor_data: return redirect(url_for('logout_route'))
    products_list = Product.query.filter_by(brand=vendor_data.brand_name).all()
    return render_template('dashboard.html', vendor=vendor_data, products=products_list)

# ==========================================
# --- مسارات الإدارة المركزية (Admin) ---
# ==========================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login_route():
    # إذا كان المدير مسجلاً دخوله بالفعل، انقله للداشبورد فوراً
    if is_admin_logged_in(): 
        return redirect(url_for('admin_dashboard_route'))
    
    if request.method == 'POST':
        u = request.form.get('admin_user')
        p = request.form.get('admin_pass')
        if verify_admin_credentials(u, p):
            return redirect(url_for('admin_dashboard_route'))
            
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard_route():
    if not is_admin_logged_in(): 
        return redirect(url_for('admin_login_route'))
    
    # جلب البيانات لبرج المراقبة
    all_vendors = Vendor.query.all()
    pending_products = Product.query.filter_by(status='pending').all()
    
    return render_template('admin_dashboard.html', 
                           vendors=all_vendors, 
                           pending_count=len(pending_products))

@app.route('/admin/logout')
def admin_logout():
    logout_admin_logic() 
    return redirect(url_for('admin_login_route'))

# --- تسجيل الخروج العام ---
@app.route('/logout')
def logout_route():
    session.clear() 
    flash("تم تسجيل الخروج من النظام اللامركزي.", "info")
    return redirect(url_for('login_page'))

# --- تشغيل السيرفر ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
