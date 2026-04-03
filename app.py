import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

# --- 1. استدعاء ملفاتك الجاهزة (يجب أن تتطابق الأسماء) ---
from config import Config
from database import db, init_db
from models import Product, Vendor, AdminUser, seed_admin
# استيراد الدوال حسب مسمياتك في logic.py
from logic import login_vendor, is_logged_in 

# --- 2. تعريف التطبيق السيادي ---
app = Flask(__name__)
app.config.from_object(Config)

# إعدادات الرفع
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- 3. تهيئة القاعدة وتحديث الهيكل ---
init_db(app)

with app.app_context():
    # تحديث الجداول لإنهاء خطأ column vendor.status does not exist
    db.create_all() 
    # حقن بيانات "علي محجوب"
    seed_admin() 

# --- 4. حراس البوابات (Security Guards) ---
def is_admin_logged_in():
    return session.get('role') == 'admin' and 'admin_id' in session

# ==========================================
# --- 5. المسارات (Routes) المترابطة ---
# ==========================================

@app.route('/')
def home():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard'))
    if is_logged_in(): return redirect(url_for('vendor_dashboard')) # استخدام دالتك
    return redirect(url_for('login_page'))

# بوابة دخول المورد
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in(): return redirect(url_for('vendor_dashboard'))
    
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        # استدعاء دالتك بالاسم الصحيح: login_vendor
        success, message = login_vendor(u, p)
        
        if success:
            flash(message, "success")
            return redirect(url_for('vendor_dashboard'))
        else:
            flash(message, "danger")
            
    return render_template('login.html')

# لوحة تحكم المورد
@app.route('/dashboard')
def vendor_dashboard():
    if not is_logged_in(): return redirect(url_for('login_page'))
    
    vendor = Vendor.query.get(session.get('user_id'))
    products = Product.query.filter_by(vendor_id=vendor.id).all()
    return render_template('dashboard.html', vendor=vendor, products=products)

# بوابة دخول الإدارة (برج المراقبة)
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        # هنا سنفترض وجود دالة verify_admin في logic أو نتحقق مباشرة
        u = request.form.get('admin_user', '').strip()
        p = request.form.get('admin_pass', '').strip()
        
        admin = AdminUser.query.filter_by(username=u).first()
        from werkzeug.security import check_password_hash
        if admin and check_password_hash(admin.password, p):
            session.clear()
            session['admin_id'] = admin.id
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        flash("بيانات دخول برج المراقبة غير صحيحة.", "danger")
            
    return render_template('admin_login.html')

# لوحة تحكم الإدارة
@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin_logged_in(): return redirect(url_for('admin_login'))
    all_vendors = Vendor.query.all()
    return render_template('admin_dashboard.html', vendors=all_vendors)

# تسجيل الخروج
@app.route('/logout')
def logout():
    session.clear() # تنظيف الجلسة السيادية
    flash("تم تأمين البوابات.", "info")
    return redirect(url_for('login_page'))

# --- 6. التشغيل النهائي ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
