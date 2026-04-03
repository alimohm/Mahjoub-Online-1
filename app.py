import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

# --- [1] استيراد المحركات والإعدادات ---
from config import Config
from database import db, init_db
from models import Vendor, AdminUser, Product, seed_admin

# استيراد منطق البوابات (الذي يفرق بين عدم التسجيل وخطأ الباسورد)
from logic import login_vendor, is_logged_in
from admin_logic import verify_admin_credentials, is_admin_logged_in

app = Flask(__name__)
app.config.from_object(Config)

# ربط قاعدة البيانات Postgres في Railway
init_db(app)

# --- [2] تهيئة النظام وحقن البيانات (علي محجوب / 123) ---
with app.app_context():
    db.create_all() 
    seed_admin() 

# --- [3] توجيه الرابط الرئيسي (Smart Redirect) ---
@app.route('/')
def index():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard'))
    if is_logged_in(): return redirect(url_for('vendor_dashboard'))
    return redirect(url_for('login_page'))

# --- [4] 🏛️ قسم الإدارة المركزية (برج المراقبة) ---

# الرابط: /admin/login (صفحة تسجيل دخول الإدارة)
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        # استخدام الحقول admin_user و admin_pass كما في تصميمك
        u = request.form.get('admin_user')
        p = request.form.get('admin_pass')
        
        success, msg = verify_admin_credentials(u, p)
        if success:
            flash(msg, "success")
            return redirect(url_for('admin_dashboard'))
        
        # هنا ستظهر رسالة: "غير مسجل ضمن طاقم الإدارة" أو "خطأ في كلمة المرور"
        flash(msg, "danger")
        
    return render_template('admin_login.html')

# الرابط: /admin/dashboard (لوحة التحكم المركزية)
@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin_logged_in(): return redirect(url_for('admin_login'))
    
    vendors = Vendor.query.all()
    products = Product.query.all()
    return render_template('admin_dashboard.html', vendors=vendors, products=products)


# --- [5] 📦 قسم الموردين (المنصة اللامركزية) ---

# الرابط: /login (بوابة دخول الموردين العادية)
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in(): return redirect(url_for('vendor_dashboard'))
    
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        
        success, msg = login_vendor(u, p)
        if success:
            flash(msg, "success")
            return redirect(url_for('vendor_dashboard'))
        
        # هنا ستظهر رسالة: "غير مسجل في المنصة اللامركزية" أو "خطأ كلمة المرور"
        flash(msg, "danger")
        
    return render_template('login.html')

# الرابط: /dashboard (لوحة تحكم المورد)
@app.route('/dashboard')
def vendor_dashboard():
    if not is_logged_in(): return redirect(url_for('login_page'))
    
    vendor = Vendor.query.get(session.get('user_id'))
    products = Product.query.filter_by(vendor_id=vendor.id).all()
    return render_template('dashboard.html', vendor=vendor, products=products)


# --- [6] الخروج وتأمين النظام ---
@app.route('/logout')
def logout():
    session.clear()
    flash("تم تأمين الجلسة وقطع الاتصال بنجاح.", "info")
    return redirect(url_for('login_page'))

# التشغيل المتوافق مع Railway
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
