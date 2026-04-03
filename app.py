import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

# --- 1. تهيئة التطبيق والقضاء على أخطاء الاستيراد ---
app = Flask(__name__)

from config import Config
from database import db, init_db
from models import Product, Vendor, AdminUser, seed_admin

# استيراد منطق البوابات (admin للإدارة، وما دونه للمورد)
from logic import login_vendor, is_logged_in 
from admin_logic import verify_admin_credentials, is_admin_logged_in

# تحميل الإعدادات وربط القاعدة
app.config.from_object(Config)
init_db(app)

# القوة الضاربة: تحديث الجداول وحقن البيانات فور الإقلاع
with app.app_context():
    # تحديث الأعمدة (status, wallet_address) في Postgres
    db.create_all() 
    # تأمين وجود حساباتك (علي محجوب) بكلمة مرور 123
    seed_admin() 

# ==========================================
# --- بوابات تسجيل الدخول (Login Routes) ---
# ==========================================

# [1] بوابة دخول المورد (مطابقة لملف login.html)
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

# [2] بوابة دخول الإدارة (مطابقة لملف admin_login.html)
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_admin_logged_in(): 
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        # الأسماء admin_user و admin_pass مطابقة للفورم الذي أرسلته
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

# لوحة المورد (عرض المنتجات والمحفظة)
@app.route('/dashboard')
def vendor_dashboard():
    if not is_logged_in(): 
        return redirect(url_for('login_page'))
    
    vendor = Vendor.query.get(session.get('user_id'))
    if not vendor: return redirect(url_for('logout'))
    
    products = Product.query.filter_by(vendor_id=vendor.id).all()
    return render_template('dashboard.html', vendor=vendor, products=products)

# لوحة الإدارة (برج المراقبة للتحكم الشامل)
@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin_logged_in(): 
        return redirect(url_for('admin_login'))
    
    all_vendors = Vendor.query.all()
    pending_products = Product.query.filter_by(status='pending').all()
    return render_template('admin_dashboard.html', 
                           vendors=all_vendors, 
                           pending_count=len(pending_products))

# ==========================================
# --- التوجيه السيادي والخروج ---
# ==========================================

@app.route('/')
def index():
    # التوجيه التلقائي حسب الرتبة المخزنة في الجلسة
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard'))
    if is_logged_in(): return redirect(url_for('vendor_dashboard'))
    return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    session.clear()
    flash("تم تأمين كافة الأنظمة الرقمية بنجاح.", "info")
    return redirect(url_for('login_page'))

# تشغيل السيرفر بتوافق Railway
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
