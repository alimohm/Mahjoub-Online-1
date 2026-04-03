import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

# --- 1. تعريف التطبيق والتهيئة ---
app = Flask(__name__)

from config import Config
from database import db, init_db
from models import Product, Vendor, AdminUser, seed_admin

# استيراد المنطق (قاعدتنا: admin للإدارة، وما دونه للمورد)
from logic import login_vendor, is_logged_in 
from admin_logic import verify_admin_credentials, is_admin_logged_in

app.config.from_object(Config)
init_db(app)

with app.app_context():
    db.create_all() # تحديث الجداول فوراً
    seed_admin()    # حقن بيانات علي محجوب (123)

# ==========================================
# --- بوابات تسجيل الدخول (Login Routes) ---
# ==========================================

# [1] بوابة دخول المورد (Vendor Login)
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in(): 
        return redirect(url_for('vendor_dashboard'))
    
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        success, message = login_vendor(u, p)
        if success:
            flash(message, "success")
            return redirect(url_for('vendor_dashboard'))
        flash(message, "danger")
            
    return render_template('login.html')

# [2] بوابة دخول الإدارة (Admin Login)
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_admin_logged_in(): 
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        # لاحظ الأسماء هنا يجب أن تطابق ملف admin_login.html
        u = request.form.get('admin_user', '').strip()
        p = request.form.get('admin_pass', '').strip()
        
        success, message = verify_admin_credentials(u, p)
        if success:
            flash(message, "success")
            return redirect(url_for('admin_dashboard'))
        flash(message, "danger")
            
    return render_template('admin_login.html')

# ==========================================
# --- لوحات التحكم (Dashboards) ---
# ==========================================

# لوحة المورد
@app.route('/dashboard')
def vendor_dashboard():
    if not is_logged_in(): 
        return redirect(url_for('login_page'))
    vendor = Vendor.query.get(session.get('user_id'))
    return render_template('dashboard.html', vendor=vendor)

# لوحة الإدارة
@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin_logged_in(): 
        return redirect(url_for('admin_login'))
    all_vendors = Vendor.query.all()
    return render_template('admin_dashboard.html', vendors=all_vendors)

# ==========================================
# --- الهيكل العام والتوجيه ---
# ==========================================

@app.route('/')
def index():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard'))
    if is_logged_in(): return redirect(url_for('vendor_dashboard'))
    return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    session.clear()
    flash("تم تأمين الخروج بنجاح.", "info")
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
