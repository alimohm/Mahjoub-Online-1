import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

# 1. استيراد الإعدادات والمحرك وقاعدة البيانات
from config import Config
from database import db, init_db
from models import Vendor, AdminUser, Product, seed_admin

# 2. استيراد المنطق البرمجي للبوابات (من الملفات التي أصلحناها)
from logic import login_vendor, is_logged_in
from admin_logic import verify_admin_credentials, is_admin_logged_in

app = Flask(__name__)
app.config.from_object(Config)

# ربط التطبيق بقاعدة البيانات Postgres في Railway
init_db(app)

# 3. تهيئة النظام: إنشاء الجداول وحقن بيانات "علي محجوب"
with app.app_context():
    # سيقوم هذا السطر ببناء الجداول (vendor, admin_user, product) 
    # بالهيكل الجديد المحدث فور حذف القديمة.
    db.create_all() 
    
    # إضافة بيانات المدير الافتراضية (علي محجوب / 123)
    seed_admin() 

# --- [ البوابات والروابط ] ---

@app.route('/')
def index():
    """التوجيه التلقائي حسب نوع الحساب"""
    if is_admin_logged_in():
        return redirect(url_for('admin_dashboard'))
    if is_logged_in():
        return redirect(url_for('vendor_dashboard'))
    return redirect(url_for('login_page'))

# بوابة دخول الموردين
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in():
        return redirect(url_for('vendor_dashboard'))
    
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        success, msg = login_vendor(u, p)
        if success:
            return redirect(url_for('vendor_dashboard'))
        flash(msg, "danger")
    return render_template('login.html')

# بوابة دخول الإدارة المركزية
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_admin_logged_in():
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        # مطابقة الأسماء admin_user و admin_pass لملف HTML الخاص بك
        u = request.form.get('admin_user')
        p = request.form.get('admin_pass')
        success, msg = verify_admin_credentials(u, p)
        if success:
            return redirect(url_for('admin_dashboard'))
        flash(msg, "danger")
    return render_template('admin_login.html')

# --- [ لوحات التحكم ] ---

@app.route('/dashboard')
def vendor_dashboard():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    vendor = Vendor.query.get(session.get('user_id'))
    products = Product.query.filter_by(vendor_id=vendor.id).all()
    return render_template('dashboard.html', vendor=vendor, products=products)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))
    
    all_vendors = Vendor.query.all()
    all_products = Product.query.all()
    return render_template('admin_dashboard.html', vendors=all_vendors, products=all_products)

# تسجيل الخروج وتأمين الجلسة
@app.route('/logout')
def logout():
    session.clear()
    flash("تم تسجيل الخروج بنجاح.", "success")
    return redirect(url_for('login_page'))

# 4. التشغيل المتوافق مع بيئة Railway
if __name__ == '__main__':
    # جلب المنفذ PORT من بيئة النظام لضمان عدم حدوث Crash
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
