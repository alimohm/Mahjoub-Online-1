import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

# --- [1] استيراد المحركات والإعدادات ---
from config import Config
from database import db, init_db
from models import Vendor, AdminUser, Product, seed_admin

# --- [2] استيراد المنطق (تأكد من وجود الدوال في الملفات المقابلة) ---
try:
    from logic import login_vendor, is_logged_in
    from admin_logic import verify_admin_credentials, is_admin_logged_in
except ImportError as e:
    print(f"❌ خطأ في الاستيراد: {e}")
    # هذا السطر سيخبرك في السجلات (Logs) أي دالة بالضبط مفقودة

app = Flask(__name__)
app.config.from_object(Config)

# ربط قاعدة البيانات
init_db(app)

# --- [3] تهيئة النظام (بناء الجداول وحقن علي محجوب) ---
with app.app_context():
    db.create_all() 
    seed_admin() 

# --- [4] المسارات الرسمية (Routes) ---

@app.route('/')
def index():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard'))
    if is_logged_in(): return redirect(url_for('vendor_dashboard'))
    return redirect(url_for('login_page'))

# بوابة دخول الموردين
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in(): return redirect(url_for('vendor_dashboard'))
    if request.method == 'POST':
        u, p = request.form.get('username'), request.form.get('password')
        success, msg = login_vendor(u, p)
        if success:
            flash(msg, "success")
            return redirect(url_for('vendor_dashboard'))
        flash(msg, "danger")
    return render_template('login.html')

# بوابة دخول الإدارة المركزية
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        u, p = request.form.get('admin_user'), request.form.get('admin_pass')
        success, msg = verify_admin_credentials(u, p)
        if success:
            flash(msg, "success")
            return redirect(url_for('admin_dashboard'))
        flash(msg, "danger")
    return render_template('admin_login.html')

# لوحات التحكم
@app.route('/dashboard')
def vendor_dashboard():
    if not is_logged_in(): return redirect(url_for('login_page'))
    vendor = Vendor.query.get(session.get('user_id'))
    return render_template('dashboard.html', vendor=vendor)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin_logged_in(): return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
