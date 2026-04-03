import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash

# --- 1. استيراد المحركات والبيانات السيادية ---
from config import Config
from database import db, init_db
from models import Product, Vendor, AdminUser, seed_admin

app = Flask(__name__)
app.config.from_object(Config)

# إعدادات رفع الوسائط (الميديا)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- 2. تفعيل قاعدة البيانات وحقن الهوية ---
init_db(app)

with app.app_context():
    # تحديث الجداول (لإضافة العمود status وتعديل الجداول في Railway)
    db.create_all()
    # حقن حساب "علي محجوب" مشفراً بكلمة مرور 123
    seed_admin() 

# ==========================================
# --- 3. وظائف التحقق (المنطق الداخلي) ---
# ==========================================

def is_logged_in():
    """التحقق من وجود جلسة مورد نشطة"""
    return session.get('role') == 'vendor' and 'user_id' in session

def is_admin_logged_in():
    """التحقق من وجود جلسة إدارة نشطة"""
    return session.get('role') == 'admin' and 'admin_id' in session

# ==========================================
# --- 4. بوابة دخول المورد (سوقك الذكي) ---
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in(): return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # استخدام strip لإزالة المسافات لضمان الدقة
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        if not u or not p:
            flash("يرجى إدخال اسم المستخدم وكلمة المرور.", "warning")
            return redirect(url_for('login_page'))

        # البحث عن المورد في القاعدة
        vendor = Vendor.query.filter_by(username=u).first()

        # التحقق الذكي (الذي طلبته)
        if not vendor:
            flash("تنبيه: اسم المستخدم هذا غير مسجل في المنصة اللامركزية.", "danger")
        elif not check_password_hash(vendor.password, p):
            flash("فشل تأمين البوابة: كلمة المرور غير صحيحة.", "danger")
        elif vendor.status == 'blocked':
            flash("وصول مرفوض: تم إيقاف هذا الحساب بقرار سيادي.", "danger")
        else:
            # تفعيل الجلسة وتأمين الدخول
            session.clear()
            session['user_id'] = vendor.id
            session['username'] = vendor.username
            session['brand'] = vendor.brand_name
            session['role'] = 'vendor'
            flash(f"أهلاً بك يا سيد {vendor.employee_name} في سوقك الذكي.", "success")
            return redirect(url_for('dashboard'))
            
    return render_template('login.html')

# ==========================================
# --- 5. بوابة دخول الإدارة (برج المراقبة) ---
# ==========================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login_route():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard_route'))
    
    if request.method == 'POST':
        u = request.form.get('admin_user', '').strip()
        p = request.form.get('admin_pass', '').strip()
        
        admin = AdminUser.query.filter_by(username=u).first()
        
        if admin and check_password_hash(admin.password, p):
            session.clear()
            session['admin_id'] = admin.id
            session['admin_user'] = admin.username
            session['role'] = 'admin'
            flash("مرحباً بك يا سيد علي في برج المراقبة.", "success")
            return redirect(url_for('admin_dashboard_route'))
        else:
            flash("بيانات دخول برج المراقبة غير صحيحة.", "danger")
            
    return render_template('admin_login.html')

# ==========================================
# --- 6. لوحات التحكم (الاستدعاءات السيادية) ---
# ==========================================

@app.route('/dashboard')
def dashboard():
    if not is_logged_in(): return redirect(url_for('login_page'))
    
    vendor_data = Vendor.query.get(session.get('user_id'))
    if not vendor_data:
        session.clear()
        return redirect(url_for('login_page'))
        
    # استدعاء منتجات المورد بناءً على معرفه الفريد (Vendor ID)
    products_list = Product.query.filter_by(vendor_id=vendor_data.id).all()
    return render_template('dashboard.html', vendor=vendor_data, products=products_list)

@app.route('/admin/dashboard')
def admin_dashboard_route():
    if not is_admin_logged_in(): return redirect(url_for('admin_login_route'))
    
    # جلب كافة الموردين والمنتجات التي تنتظر الاعتماد
    all_vendors = Vendor.query.all()
    pending_items = Product.query.filter_by(status='pending').all()
    
    return render_template('admin_dashboard.html', 
                           vendors=all_vendors, 
                           pending_items=pending_items)

# ==========================================
# --- 7. التوجيه النهائي وتأمين الخروج ---
# ==========================================

@app.route('/')
def home_redirect():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard_route'))
    if is_logged_in(): return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/logout')
def logout_route():
    session.clear()
    flash("تم تأمين البوابات بنجاح. في أمان الله.", "info")
    return redirect(url_for('login_page'))

# --- تشغيل المحرك الرقمي ---
if __name__ == '__main__':
    # التشغيل على المنفذ 8080 المعتمد لخدمات Railway السحابية
    app.run(host='0.0.0.0', port=8080, debug=True)
