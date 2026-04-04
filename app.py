import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db
import models

# استدعاء المنطق البرمجي المطور
from vendor_logic import login_vendor 
from admin_logic import verify_admin_credentials

app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

# --- [ منطقة السيادة: بناء القاعدة وحقن البيانات ] ---
with app.app_context():
    try:
        db.create_all() 
        models.seed_system()
        print("✅ تم فحص القاعدة وتوليد المحافظ السيادية بنجاح.")
    except Exception as e:
        print(f"❌ خطأ في القاعدة: {e}")

# --- [ التوجيهات العامة ] ---
@app.route('/')
def index():
    return redirect(url_for('vendor_login'))

@app.route('/logout')
def logout():
    session.clear()
    flash("تم الخروج من النظام السيادي بنجاح.", "info")
    return redirect(url_for('vendor_login'))

# --- [ بوابة الإدارة: إدارة الحسابات والاعتماد ] ---

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'super_admin':
        flash("🚫 محاولة دخول غير مصرحة لبرج المراقبة!", "danger")
        return redirect(url_for('admin_login'))
    
    # جلب جميع الموردين لعرضهم في جدول الاعتماد
    all_vendors = models.Vendor.query.all()
    return render_template('admin_accounts.html', 
                           username=session.get('username'), 
                           vendors=all_vendors)

@app.route('/admin/create-vendor', methods=['POST'])
def create_vendor():
    if session.get('role') != 'super_admin': return redirect(url_for('admin_login'))
    
    u = request.form.get('username', '').strip()
    b = request.form.get('brand_name', '').strip()
    p = request.form.get('password', '').strip()

    if models.Vendor.query.filter_by(username=u).first():
        flash("⚠️ اسم المستخدم هذا موجود مسبقاً في النظام.", "warning")
    else:
        try:
            # إنشاء المورد الجديد
            new_v = models.Vendor(username=u, brand_name=b, password=p)
            db.session.add(new_v)
            db.session.flush() # للحصول على ID المورد قبل الـ commit

            # توليد المحفظة السيادية آلياً
            import random
            wallet_num = f"MAH-{random.randint(100,999)}-{random.randint(1000,9999)}"
            new_wallet = models.Wallet(wallet_number=wallet_num, balance=0.0, vendor_id=new_v.id)
            db.session.add(new_wallet)
            
            db.session.commit()
            flash(f"✅ تم اعتماد المورد '{b}' وتفعيل محفظته بنجاح.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"❌ فشل الاعتماد: {str(e)}", "danger")
            
    return redirect(url_for('admin_dashboard'))

# --- [ بوابة الموردين: إضافة وحفظ المنتجات ] ---
@app.route('/vendor/add-product', methods=['GET', 'POST'])
def add_product():
    allowed_roles = ['vendor_owner', 'vendor_staff']
    if 'role' not in session or session.get('role') not in allowed_roles:
        flash("🚫 يرجى تسجيل الدخول كمورد للوصول لهذه الصفحة", "danger")
        return redirect(url_for('vendor_login'))
    
    vendor_data = models.Vendor.query.filter_by(username=session.get('username')).first()

    if request.method == 'POST':
        try:
            new_product = models.Product(
                name=request.form.get('name'),
                brand=request.form.get('brand'),
                price=float(request.form.get('price', 0)),
                currency=request.form.get('currency'),
                stock=int(request.form.get('stock', 1)),
                description=request.form.get('description'),
                vendor_id=vendor_data.id if vendor_data else None,
                status='pending'
            )
            db.session.add(new_product)
            db.session.commit()
            flash("🚀 تم رفع المنتج بنجاح! هو الآن بانتظار مراجعة الإدارة العليا.", "success")
            return redirect(url_for('vendor_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f"❌ حدث خطأ أثناء الرفع: {str(e)}", "danger")

    return render_template('vendor_add_product.html', vendor=vendor_data)

# --- [ مراجعة المنتجات واعتمادها ] ---
@app.route('/admin/approve-products')
def approve_products():
    if session.get('role') != 'super_admin': return redirect(url_for('admin_login'))
    pending_items = models.Product.query.filter_by(status='pending').all()
    return render_template('admin_approve.html', products=pending_items)

@app.route('/admin/action-product/<int:product_id>/<string:action>')
def product_action(product_id, action):
    if session.get('role') != 'super_admin': return redirect(url_for('admin_login'))
    product = models.Product.query.get_or_404(product_id)
    product.status = 'approved' if action == 'approve' else 'rejected'
    db.session.commit()
    flash(f"✅ تم تحديث حالة المنتج: {product.name}", "success")
    return redirect(url_for('approve_products'))

# --- [ بوابة تسجيل الدخول ] ---
@app.route('/vendor/login', methods=['GET', 'POST'])
def vendor_login():
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        success, msg, role = login_vendor(u, p) 
        if success:
            session['username'] = u
            session['role'] = role
            flash(msg, "success")
            return redirect(url_for('vendor_dashboard'))
        flash(msg, "danger")
    return render_template('login_vendor.html')

@app.route('/vendor/dashboard')
def vendor_dashboard():
    allowed_roles = ['vendor_owner', 'vendor_staff']
    if 'role' not in session or session.get('role') not in allowed_roles:
        return redirect(url_for('vendor_login'))
    
    vendor_data = models.Vendor.query.filter_by(username=session.get('username')).first()
    wallet_no = vendor_data.wallet.wallet_number if vendor_data and vendor_data.wallet else "غير متوفر"
    balance = vendor_data.wallet.balance if vendor_data and vendor_data.wallet else 0.0
    
    return render_template('vendor_dashboard.html', 
                           username=session.get('username'),
                           vendor=vendor_data,
                           wallet_no=wallet_no,
                           balance=balance,
                           show_wallet=(session.get('role') == 'vendor_owner'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        success, msg = verify_admin_credentials(u, p)
        if success:
            session['username'] = u
            session['role'] = 'super_admin'
            flash(msg, "success")
            return redirect(url_for('admin_dashboard'))
        flash(msg, "danger")
    return render_template('login_admin.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
