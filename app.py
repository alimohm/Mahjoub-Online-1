import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

# --- 1. تعريف التطبيق أولاً (لحل خطأ NameError) ---
app = Flask(__name__)

# --- 2. استدعاء الإعدادات والقاعدة ---
from config import Config
from database import db, init_db
from models import Product, Vendor, AdminUser, seed_admin

app.config.from_object(Config)
init_db(app)

# --- 3. استدعاء المنطق من ملفاتك المتعددة (حل التضارب) ---
from logic import login_vendor, is_logged_in
from admin_logic import verify_admin_credentials # تأكد أن هذا المسمى في ملف admin_logic.py
# من جسر الربط إذا لزم الأمر
# from bridge_logic import your_function 

with app.app_context():
    db.create_all() # لتجنب خطأ UndefinedColumn
    seed_admin()

# --- 4. المسارات (Routes) ---

@app.route('/')
def home():
    if session.get('role') == 'admin': return redirect(url_for('admin_dashboard'))
    if is_logged_in(): return redirect(url_for('vendor_dashboard'))
    return redirect(url_for('login_page'))

# بوابة دخول المورد (تستخدم logic.py)
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

# بوابة دخول الإدارة (تستخدم admin_logic.py)
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        u = request.form.get('admin_user', '').strip()
        p = request.form.get('admin_pass', '').strip()
        success, message = verify_admin_credentials(u, p)
        if success:
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        flash(message, "danger")
    return render_template('admin_login.html')

@app.route('/dashboard')
def vendor_dashboard():
    if not is_logged_in(): return redirect(url_for('login_page'))
    vendor = Vendor.query.get(session.get('user_id'))
    products = Product.query.filter_by(vendor_id=vendor.id).all()
    return render_template('dashboard.html', vendor=vendor, products=products)

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin': return redirect(url_for('admin_login'))
    vendors = Vendor.query.all()
    return render_template('admin_dashboard.html', vendors=vendors)

@app.route('/logout')
def logout():
    session.clear()
    flash("تم تأمين البوابات بنجاح.", "info")
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
