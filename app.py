import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

# 1. استيراد المحركات (تأكد من ترتيب الاستيراد لمنع التداخل)
from config import Config
from database import db, init_db
from models import Vendor, AdminUser, Product, seed_admin

# 2. استيراد المنطق المطور (الذي يستخدم .strip والرسائل الدقيقة)
from logic import login_vendor, is_logged_in
from admin_logic import verify_admin_credentials, is_admin_logged_in

app = Flask(__name__)
app.config.from_object(Config)

# ربط قاعدة البيانات Postgres
init_db(app)

# 3. تهيئة الجداول وحقن البيانات العربية (علي محجوب / محجوب أونلاين)
with app.app_context():
    # هذا السطر مهم جداً لإنشاء الحسابات العربية فوراً
    db.create_all() 
    seed_admin() 

# --- [ البوابات والروابط ] ---

@app.route('/')
def index():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard'))
    if is_logged_in(): return redirect(url_for('vendor_dashboard'))
    return redirect(url_for('login_page'))

# 📦 بوابة الموردين (محجوب أونلاين)
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in(): return redirect(url_for('vendor_dashboard'))
    
    if request.method == 'POST':
        # أخذ البيانات من حقول الـ HTML
        u = request.form.get('username')
        p = request.form.get('password')
        
        success, msg = login_vendor(u, p)
        if success:
            flash(msg, "success")
            return redirect(url_for('vendor_dashboard'))
        else:
            flash(msg, "danger")
            
    return render_template('login.html')

# 🏛️ بوابة الإدارة (علي محجوب)
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        # التأكد من أسماء الحقول في ملف admin_login.html
        u = request.form.get('admin_user')
        p = request.form.get('admin_pass')
        
        success, msg = verify_admin_credentials(u, p)
        if success:
            flash(msg, "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash(msg, "danger")
            
    return render_template('admin_login.html')

# --- [ لوحات التحكم ] ---

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
    flash("تم تسجيل الخروج بنجاح.", "info")
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
