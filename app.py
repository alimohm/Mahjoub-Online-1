import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

# --- [1] استيراد الإعدادات والمحركات ---
from config import Config
from database import db, init_db
from models import Vendor, AdminUser, Product, seed_admin

# استيراد المنطق البرمجي للبوابات (تم فصلها لتجنب التداخل الدائري)
from logic import login_vendor, is_logged_in
from admin_logic import verify_admin_credentials, is_admin_logged_in

app = Flask(__name__)
app.config.from_object(Config)

# ربط قاعدة البيانات Postgres الموضحة في حسابك
init_db(app)

# --- [2] تهيئة النظام وحقن البيانات السيادية ---
with app.app_context():
    # إنشاء الجداول وتحديث الأعمدة المفقودة (status, wallet_address)
    db.create_all() 
    # حقن حساب "علي محجوب" كمدير وحساب "ali_mahjoub" كمورد افتراضي
    seed_admin() 

# --- [3] بوابات تسجيل الدخول (Login Routes) ---

@app.route('/')
def index():
    """التوجيه الذكي حسب الرتبة"""
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard'))
    if is_logged_in(): return redirect(url_for('vendor_dashboard'))
    return redirect(url_for('login_page'))

# بوابة المورد
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in(): return redirect(url_for('vendor_dashboard'))
    
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        success, msg = login_vendor(u, p)
        if success:
            return redirect(url_for('vendor_dashboard'))
        flash(msg, "danger")
    return render_template('login.html')

# بوابة الإدارة المركزية (برج المراقبة)
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        # استخدام الأسماء admin_user و admin_pass المطابقة لملف HTML
        u = request.form.get('admin_user')
        p = request.form.get('admin_pass')
        success, msg = verify_admin_credentials(u, p)
        if success:
            return redirect(url_for('admin_dashboard'))
        flash(msg, "danger")
    return render_template('admin_login.html')

# --- [4] لوحات التحكم (Dashboards) ---

@app.route('/dashboard')
def vendor_dashboard():
    if not is_logged_in(): return redirect(url_for('login_page'))
    
    # جلب بيانات المورد الحالي لملء اللوحة
    vendor = Vendor.query.get(session.get('user_id'))
    products = Product.query.filter_by(vendor_id=vendor.id).all()
    return render_template('dashboard.html', vendor=vendor, products=products)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin_logged_in(): return redirect(url_for('admin_login'))
    
    # جلب إحصائيات سريعة لبرج المراقبة
    vendors_count = Vendor.query.count()
    pending_products = Product.query.filter_by(status='pending').all()
    return render_template('admin_dashboard.html', 
                           vendors_count=vendors_count, 
                           pending_products=pending_products)

# --- [5] الخروج وتأمين الأنظمة ---

@app.route('/logout')
def logout():
    session.clear()
    flash("تم تسجيل الخروج بنجاح وتأمين الجلسة.", "success")
    return redirect(url_for('login_page'))

# --- [6] التشغيل المتوافق مع Railway ---
if __name__ == '__main__':
    # استخدام المنفذ الديناميكي لـ Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
