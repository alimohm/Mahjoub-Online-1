import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

# 1. استيراد المحركات وقاعدة البيانات والموديلات
from config import Config
from database import db, init_db
from models import Vendor, AdminUser, Product, seed_admin

# 2. استيراد المنطق المطور (المسميات الجديدة والمحدثة)
from vendor_logic import login_vendor, is_logged_in
from admin_logic import verify_admin_credentials, is_admin_logged_in

app = Flask(__name__)
app.config.from_object(Config)

# ربط وتهيئة قاعدة البيانات
init_db(app)

# 3. تهيئة الجداول وحقن البيانات العربية (علي محجوب / محجوب أونلاين)
with app.app_context():
    # إنشاء الجداول إذا لم تكن موجودة
    db.create_all() 
    # حقن بيانات الإدارة والمورد الرسمي فوراً
    seed_admin() 

# --- [ التوجيه الذكي للمنصة ] ---

@app.route('/')
def index():
    # إذا كان المسؤول مسجلاً دخوله يذهب للوحة الإدارة
    if is_admin_logged_in(): 
        return redirect(url_for('admin_dashboard'))
    # إذا كان المورد مسجلاً دخوله يذهب للوحة الموردين
    if is_logged_in(): 
        return redirect(url_for('vendor_dashboard'))
    # الافتراضي: التوجه لبوابة الموردين
    return redirect(url_for('vendor_login'))

# --- [ 📦 بوابة الموردين: محجوب أونلاين ] ---

@app.route('/vendor/login', methods=['GET', 'POST'])
def vendor_login():
    if is_logged_in(): 
        return redirect(url_for('vendor_dashboard'))
    
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        success, msg = login_vendor(u, p)
        if success:
            flash(msg, "success")
            return redirect(url_for('vendor_dashboard'))
        else:
            flash(msg, "danger")
            
    return render_template('vendor_login.html')

@app.route('/vendor/dashboard')
def vendor_dashboard():
    # حماية المسار: لا يمكن الدخول بدون تسجيل دخول المورد
    if not is_logged_in(): 
        return redirect(url_for('vendor_login'))
    
    vendor = Vendor.query.get(session.get('user_id'))
    return render_template('dashboard.html', vendor=vendor)

# --- [ 🏛️ بوابة الإدارة: علي محجوب ] ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_admin_logged_in(): 
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        # استخدام الحقول المخصصة للإدارة
        u = request.form.get('admin_user', '').strip()
        p = request.form.get('admin_pass', '').strip()
        
        success, msg = verify_admin_credentials(u, p)
        if success:
            flash(msg, "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash(msg, "danger")
            
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    # حماية المسار: لا يمكن الدخول بدون تسجيل دخول الإدارة
    if not is_admin_logged_in(): 
        return redirect(url_for('admin_login'))
    
    return render_template('admin_dashboard.html')

# --- [ بوابة إضافة المنتجات ] ---

@app.route('/vendor/add-product', methods=['GET', 'POST'])
def add_product():
    if not is_logged_in():
        return redirect(url_for('vendor_login'))
    
    vendor = Vendor.query.get(session.get('user_id'))
    
    if request.method == 'POST':
        # منطق إضافة المنتج (يمكنك استدعاء دالة من vendor_logic هنا)
        flash("تم استلام بيانات المنتج بنجاح", "success")
        return redirect(url_for('vendor_dashboard'))
        
    return render_template('add_product.html', vendor=vendor)

# --- [ الخروج الآمن ] ---

@app.route('/logout')
def logout_route():
    session.clear()
    flash("تم تسجيل الخروج بنجاح وتأمين الجلسة.", "info")
    return redirect(url_for('vendor_login'))

if __name__ == '__main__':
    # تشغيل التطبيق على المنفذ 8080 بما يتوافق مع بيئة السحاب
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
