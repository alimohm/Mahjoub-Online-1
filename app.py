import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db
import models

# استدعاء المنطق البرمجي (تأكد من مطابقة الأسماء في admin_logic.py)
from vendor_logic import login_vendor 
from admin_logic import (
    verify_admin_credentials, 
    manage_accounts_logic, 
    create_vendor_logic, 
    get_admin_stats
)

# 1. تعريف التطبيق (أساسي في هذا الموقع ليتمكن Gunicorn من العثور عليه)
app = Flask(__name__)
app.config.from_object(Config)

# 2. تهيئة قاعدة البيانات
init_db(app)

# --- [ منطقة السيادة: بناء الهيكل وحقن البيانات ] ---
with app.app_context():
    try:
        db.create_all() 
        models.seed_system()
        print("✅ نظام محجوب أونلاين: القاعدة جاهزة والمحافظ السيادية مُفعلة.")
    except Exception as e:
        print(f"❌ خطأ في تهيئة النظام: {e}")

# --- [ التوجيهات العامة ] ---
@app.route('/')
def index():
    role = session.get('role')
    if role == 'super_admin':
        return redirect(url_for('admin_dashboard'))
    elif role in ['vendor_owner', 'vendor_staff']:
        return redirect(url_for('vendor_dashboard'))
    return redirect(url_for('vendor_login'))

# --- [ بوابة الإدارة: برج المراقبة ] ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('role') == 'super_admin':
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        success, msg = verify_admin_credentials(u, p)
        if success:
            flash(msg, "success")
            return redirect(url_for('admin_dashboard'))
        flash(msg, "danger")
    return render_template('login_admin.html')

# الرابط 1: لوحة التحكم (إحصائيات فقط)
@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    stats = get_admin_stats()
    return render_template('admin_main.html', 
                           username=session.get('username'), 
                           stats=stats)

# الرابط 2: صفحة اعتماد الموردين (تم تعديل اسم الملف هنا)
@app.route('/admin/vendors-accreditation')
def vendors_accreditation():
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    all_vendors = manage_accounts_logic() 
    # التعديل: استدعاء ملف vendor_accreditation.html بدلاً من admin_accounts
    return render_template('vendor_accreditation.html', 
                           username=session.get('username'), 
                           vendors=all_vendors)

# الرابط 3: معالج إنشاء حسابات الموردين
@app.route('/admin/create-vendor', methods=['POST'])
def create_vendor_route():
    if session.get('role') != 'super_admin': 
        return redirect(url_for('admin_login'))
    
    success, msg = create_vendor_logic()
    flash(msg, "success" if success else "danger")
    # العودة لصفحة الاعتماد بعد التنفيذ
    return redirect(url_for('vendors_accreditation'))

# --- [ بوابة الموردين ] ---

@app.route('/vendor/login', methods=['GET', 'POST'])
def vendor_login():
    if session.get('role') in ['vendor_owner', 'vendor_staff']:
        return redirect(url_for('vendor_dashboard'))

    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        success, msg, role = login_vendor(u, p) 
        if success:
            session.clear()
            session.permanent = True
            session['username'] = u
            session['role'] = role
            flash(msg, "success")
            return redirect(url_for('vendor_dashboard'))
        flash(msg, "danger")
    return render_template('login_vendor.html')

@app.route('/vendor/dashboard')
def vendor_dashboard():
    role = session.get('role')
    username = session.get('username')

    if role not in ['vendor_owner', 'vendor_staff']:
        return redirect(url_for('vendor_login'))
    
    if role == 'vendor_owner':
        vendor_data = models.Vendor.query.filter_by(username=username).first()
    else:
        staff = models.VendorStaff.query.filter_by(username=username).first()
        vendor_data = staff.vendor if staff else None
    
    if not vendor_data:
        session.clear()
        return redirect(url_for('vendor_login'))

    wallet = vendor_data.wallet
    return render_template('vendor_dashboard.html', 
                           username=username,
                           vendor=vendor_data,
                           wallet_no=wallet.wallet_number if wallet else "N/A", 
                           balance=wallet.balance if wallet else 0.0)

# --- [ الخروج الآمن ] ---
@app.route('/logout')
def logout():
    role = session.get('role')
    session.clear()
    flash("تم تسجيل الخروج آلياً.", "info")
    return redirect(url_for('admin_login' if role == 'super_admin' else 'vendor_login'))

# 3. التشغيل
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
