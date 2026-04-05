import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db
import models

# استدعاء المنطق البرمجي من الملفات المساعدة
from vendor_logic import login_vendor 
from admin_logic import (
    verify_admin_credentials, 
    manage_accounts_logic, 
    create_vendor_logic, 
    get_admin_stats
)

app = Flask(__name__)
app.config.from_object(Config)

# تهيئة قاعدة البيانات وربطها بالتطبيق
init_db(app)

with app.app_context():
    try:
        db.create_all() 
        models.seed_system()
        print("✅ نظام محجوب أونلاين: السيادة التقنية جاهزة وقاعدة البيانات متصلة.")
    except Exception as e:
        print(f"❌ خطأ في تهيئة النظام: {e}")

# --- [ التوجيه الرئيسي ] ---

@app.route('/')
def index():
    role = session.get('role')
    if role == 'super_admin':
        return redirect(url_for('admin_dashboard'))
    elif role in ['vendor_owner', 'vendor_staff']:
        return redirect(url_for('vendor_dashboard'))
    return redirect(url_for('vendor_login'))

# --- [ بوابة الإدارة - Super Admin ] ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('role') == 'super_admin':
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        success, msg = verify_admin_credentials(u, p)
        if success:
            session.permanent = True
            session['username'] = u
            session['role'] = 'super_admin'
            flash(msg, "success")
            return redirect(url_for('admin_dashboard'))
        flash(msg, "danger")
    return render_template('login_admin.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    stats = get_admin_stats()
    # يفتح لوحة التحكم الرئيسية (ملخص الإحصائيات)
    return render_template('admin_main.html', 
                           username=session.get('username'), 
                           stats=stats)

@app.route('/admin/vendors-accreditation')
def vendors_accreditation():
    """هذه الدالة هي المسؤولة عن فتح صفحة إدارة الحسابات والاعتماد"""
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    # جلب قائمة الموردين من قاعدة البيانات
    all_vendors = manage_accounts_logic() 
    
    # الربط بملفك الحقيقي admin_accounts.html
    return render_template('admin_accounts.html', 
                           username=session.get('username'), 
                           vendors=all_vendors)

@app.route('/admin/create-vendor', methods=['POST'])
def create_vendor_route():
    """الدالة المسؤولة عن معالجة فورم إضافة مورد جديد"""
    if session.get('role') != 'super_admin': 
        return redirect(url_for('admin_login'))
    
    success, msg = create_vendor_logic()
    flash(msg, "success" if success else "danger")
    # بعد الإضافة، نعود لصفحة الاعتماد لرؤية المورد الجديد
    return redirect(url_for('vendors_accreditation'))

# --- [ بوابة الموردين - Vendors ] ---

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
    
    # جلب بيانات المورد ومحفظته
    vendor_data = models.Vendor.query.filter_by(username=username).first() if role == 'vendor_owner' else None
    if not vendor_data and role == 'vendor_staff':
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

# --- [ تسجيل الخروج ] ---

@app.route('/logout')
def logout():
    role = session.get('role')
    session.clear()
    flash("تم تسجيل الخروج من نظام محجوب أونلاين بنجاح.", "info")
    return redirect(url_for('admin_login' if role == 'super_admin' else 'vendor_login'))

if __name__ == '__main__':
    # إعداد المنفذ ليتوافق مع بيئة Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
