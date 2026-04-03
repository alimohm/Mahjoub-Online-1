import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# --- 1. استيراد الإعدادات والمنطق ---
from config import Config
from database import db, init_db
from models import Product, Vendor, AdminUser, seed_admin
from logic import login_vendor, is_logged_in
from admin_logic import is_admin_logged_in, verify_admin_credentials, logout_admin_logic

app = Flask(__name__)
app.config.from_object(Config)

# إعدادات الرفع
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- 2. تفعيل قاعدة البيانات وحقن الهوية (علي محجوب) ---
init_db(app)
with app.app_context():
    db.create_all()
    seed_admin() 

# ==========================================
# --- 3. مسار المورد (Dashboard) - تم التأمين ---
# ==========================================
@app.route('/dashboard')
def dashboard():
    # التأكد من أن المستخدم "مورد" وليس مديراً أو زائراً
    if not is_logged_in(): 
        return redirect(url_for('login_page'))
    
    # جلب بيانات المورد بناءً على الجلسة
    vendor_data = Vendor.query.filter_by(username=session.get('username')).first()
    
    # الخلل المحتمل كان هنا: إذا فقدت الجلسة أو لم يجد المورد
    if not vendor_data:
        flash("فشلت عملية التحقق من الهوية اللامركزية.", "danger")
        session.clear()
        return redirect(url_for('login_page'))
        
    # جلب المنتجات المرتبطة ببراند المورد
    products_list = Product.query.filter_by(brand=vendor_data.brand_name).all()
    
    # تمرير 'vendor' لكي يقرأه layout.html و 'products' لملء الجداول
    return render_template('dashboard.html', 
                           vendor=vendor_data, 
                           products=products_list)

# ==========================================
# --- 4. مسار الإدارة (برج المراقبة) ---
# ==========================================
@app.route('/admin/dashboard')
def admin_dashboard_route():
    if not is_admin_logged_in(): 
        return redirect(url_for('admin_login_route'))
    
    all_vendors = Vendor.query.all()
    pending_items = Product.query.filter_by(status='pending').all()
    
    return render_template('admin_dashboard.html', 
                           vendors=all_vendors, 
                           pending_count=len(pending_items),
                           pending_items=pending_items)

# ==========================================
# --- 5. مسارات الدخول (Login) ---
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in(): return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        if login_vendor(u, p):
            return redirect(url_for('dashboard'))
            
    return render_template('login.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login_route():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard_route'))
    
    if request.method == 'POST':
        u = request.form.get('admin_user')
        p = request.form.get('admin_pass')
        if verify_admin_credentials(u, p):
            return redirect(url_for('admin_dashboard_route'))
            
    return render_template('admin_login.html')

# ==========================================
# --- 6. العمليات المشتركة ---
# ==========================================

@app.route('/')
def home_redirect():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard_route'))
    if is_logged_in(): return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/logout')
def logout_route():
    session.clear()
    flash("تم تأمين الجلسة والخروج بنجاح.", "info")
    return redirect(url_for('login_page'))

# إضافة مسار لرفع المنتجات (لأن الهيكل يطلبه)
@app.route('/add_product')
def add_product():
    if not is_logged_in(): return redirect(url_for('login_page'))
    return "صفحة رفع المنتجات قيد البرمجة..."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
