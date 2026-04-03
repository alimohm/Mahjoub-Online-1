import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash

# --- 1. استيراد المحركات ---
from config import Config
from database import db, init_db
from models import Product, Vendor, AdminUser, seed_admin

app = Flask(__name__)
app.config.from_object(Config)

# إعداد الميديا
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- 2. تهيئة وتحديث القاعدة (الحل الجذري) ---
init_db(app)

with app.app_context():
    # ملاحظة سيادية: السطر التالي سيمسح البيانات القديمة لمرة واحدة فقط 
    # لضمان إنشاء الأعمدة الجديدة (status, wallet_address)
    # db.drop_all() # فك التعليق عن هذا السطر فقط إذا استمر الخطأ، ثم أعد تعليقه
    db.create_all() 
    seed_admin()

# --- 3. حراس الجلسات ---
def is_logged_in():
    return session.get('role') == 'vendor' and 'user_id' in session

def is_admin_logged_in():
    return session.get('role') == 'admin' and 'admin_id' in session

# ==========================================
# --- 4. المسارات (Routes) المضبوطة ---
# ==========================================

@app.route('/')
def home_redirect():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard_route'))
    if is_logged_in(): return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in(): return redirect(url_for('dashboard'))
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        vendor = Vendor.query.filter_by(username=u).first()
        if vendor and check_password_hash(vendor.password, p):
            if vendor.status == 'blocked':
                flash("وصول مرفوض بقرار سيادي.", "danger")
            else:
                session.clear()
                session['user_id'] = vendor.id
                session['username'] = vendor.username
                session['role'] = 'vendor'
                return redirect(url_for('dashboard'))
        else:
            flash("بيانات الدخول غير صحيحة.", "danger")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not is_logged_in(): return redirect(url_for('login_page'))
    vendor_data = Vendor.query.get(session.get('user_id'))
    products_list = Product.query.filter_by(vendor_id=vendor_data.id).all()
    return render_template('dashboard.html', vendor=vendor_data, products=products_list)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login_route():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard_route'))
    if request.method == 'POST':
        u = request.form.get('admin_user', '').strip()
        p = request.form.get('admin_pass', '').strip()
        admin = AdminUser.query.filter_by(username=u).first()
        if admin and check_password_hash(admin.password, p):
            session.clear()
            session['admin_id'] = admin.id
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard_route'))
        flash("فشل الدخول لبرج المراقبة.", "danger")
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard_route():
    if not is_admin_logged_in(): return redirect(url_for('admin_login_route'))
    all_vendors = Vendor.query.all()
    pending_items = Product.query.filter_by(status='pending').all()
    return render_template('admin_dashboard.html', vendors=all_vendors, pending_items=pending_items)

@app.route('/logout')
def logout_route():
    session.clear()
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
