import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash

# --- 1. استيراد الإعدادات والمنطق ---
from config import Config
from database import db, init_db
from models import Product, Vendor, AdminUser, seed_admin
from logic import is_logged_in # سنقوم بتحديث المنطق داخلياً هنا
from admin_logic import is_admin_logged_in, logout_admin_logic

app = Flask(__name__)
app.config.from_object(Config)

# إعدادات الرفع (الميديا)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # حد أقصى 16 ميجا
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- 2. تفعيل قاعدة البيانات وحقن الهوية ---
init_db(app)
with app.app_context():
    db.create_all()
    seed_admin() 

# ==========================================
# --- 3. بوابة دخول المورد (تأمين البوابة) ---
# ==========================================
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in(): return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        
        # الاستعلام من قاعدة البيانات (جدول الموردين)
        vendor = Vendor.query.filter_by(username=u).first()
        
        # 1. التحقق من الوجود
        if not vendor:
            flash("المستخدم غير مسجل في المنصة اللامركزية.", "danger")
            return redirect(url_for('login_page'))
            
        # 2. التحقق من كلمة المرور
        if not check_password_hash(vendor.password, p):
            flash("فشل تأمين البوابة: كلمة المرور غير صحيحة.", "danger")
            return redirect(url_for('login_page'))
            
        # 3. مراجعة الحالات السيادية
        status = vendor.status.lower() if vendor.status else 'pending'
        
        if status == 'blocked': # موقف / محظور
            flash("وصول مرفوض: تم حظر حسابك بقرار سيادي لمخالفة السياسات.", "danger")
            return redirect(url_for('login_page'))
            
        elif status == 'restricted': # مقيد
            flash("حساب مقيد: صلاحياتك معلقة حالياً، يرجى مراجعة إدارة السيادة.", "warning")
            return redirect(url_for('login_page'))
            
        elif status == 'pending': # تحت المراجعة
            flash("الدخول معلق: حسابك لا يزال تحت المراجعة والتدقيق الفني.", "info")
            return redirect(url_for('login_page'))
            
        elif status == 'under_surveillance': # تحت الرقابة
            session['surveillance_mode'] = True
            flash("تنبيه: أنت الآن تحت نظام الرقابة الرقمية المستمرة.", "warning")

        # 4. النجاح وتفعيل الجلسة
        session['user_id'] = vendor.id
        session['username'] = vendor.username
        session['role'] = 'vendor'
        return redirect(url_for('dashboard'))
        
    return render_template('login.html')

# ==========================================
# --- 4. بوابة دخول الإدارة (برج المراقبة) ---
# ==========================================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login_route():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard_route'))
    
    if request.method == 'POST':
        u = request.form.get('admin_user')
        p = request.form.get('admin_pass')
        
        admin = AdminUser.query.filter_by(username=u).first()
        
        if admin and check_password_hash(admin.password, p):
            session['admin_id'] = admin.id
            session['username'] = admin.username
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard_route'))
        else:
            flash("فشل تأمين بوابة الإدارة: بيانات الاعتماد غير صحيحة.", "danger")
            
    return render_template('admin_login.html')

# ==========================================
# --- 5. مسارات المورد (تستخدم layout.html) ---
# ==========================================
@app.route('/dashboard')
def dashboard():
    if not is_logged_in(): return redirect(url_for('login_page'))
    
    vendor_data = Vendor.query.filter_by(username=session.get('username')).first()
    products_list = Product.query.filter_by(brand=vendor_data.brand_name).all()
    
    # يتم العرض باستخدام الهيكل المخصص للمورد تلقائياً عبر وسم extends في الصفحة
    return render_template('dashboard.html', vendor=vendor_data, products=products_list)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if not is_logged_in(): return redirect(url_for('login_page'))
    
    vendor_data = Vendor.query.filter_by(username=session.get('username')).first()
    if request.method == 'POST':
        # (نفس منطق الرفع الذي أرسلته سابقاً دون تغيير)
        pass # ... كود الرفع الخاص بك ...
        
    return render_template('add_product.html', vendor=vendor_data)

# ==========================================
# --- 6. مسارات الإدارة (تستخدم admin_layout.html) ---
# ==========================================
@app.route('/admin/dashboard')
def admin_dashboard_route():
    if not is_admin_logged_in(): return redirect(url_for('admin_login_route'))
    
    all_vendors = Vendor.query.all()
    pending_items = Product.query.filter_by(status='pending').all()
    
    # يتم العرض باستخدام هيكل برج المراقبة
    return render_template('admin_dashboard.html', 
                           vendors=all_vendors, 
                           pending_count=len(pending_items),
                           pending_items=pending_items)

# ==========================================
# --- 7. التحكم النهائي والخروج ---
# ==========================================
@app.route('/')
def home_redirect():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard_route'))
    if is_logged_in(): return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/logout')
def logout_route():
    session.clear()
    flash("تم تأمين الجلسة والخروج بنجاح من المنصة.", "info")
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
