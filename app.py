import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# --- استيراد ملفات المشروع ---
from config import Config
from database import db, init_db
from models import Product, Vendor, AdminUser, seed_admin
from logic import login_vendor, is_logged_in
from admin_logic import is_admin_logged_in, verify_admin_credentials, logout_admin_logic

app = Flask(__name__)
app.config.from_object(Config)

# إعدادات الرفع
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

init_db(app)

with app.app_context():
    db.create_all()
    seed_admin() # إنشاء حساب صبري الافتراضي

# ==========================================
# --- مسارات الدخول (Login Routes) ---
# ==========================================

@app.route('/')
def index():
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

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login_route():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard_route'))
    if request.method == 'POST':
        u = request.form.get('admin_user')
        p = request.form.get('admin_pass')
        if verify_admin_credentials(u, p):
            return redirect(url_for('admin_dashboard_route'))
    return render_template('admin_login.html')

# ==========================================
# --- لوحات التحكم (Dashboards) ---
# ==========================================

@app.route('/dashboard')
def dashboard():
    if not is_logged_in(): return redirect(url_for('login_page'))
    vendor = Vendor.query.filter_by(username=session['username']).first()
    products = Product.query.filter_by(brand=vendor.brand_name).all()
    return render_template('dashboard.html', vendor=vendor, products=products)

@app.route('/admin/dashboard')
def admin_dashboard_route():
    if not is_admin_logged_in(): 
        return redirect(url_for('admin_login_route'))
    
    # ربط البيانات الحقيقية لبرج المراقبة
    all_vendors = Vendor.query.all()
    pending_products = Product.query.filter_by(status='pending').all()
    
    return render_template('admin_dashboard.html', 
                           vendors=all_vendors, 
                           pending_count=len(pending_products),
                           pending_items=pending_products)

# --- تشغيل السيرفر ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
