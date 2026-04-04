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

# --- [ بوابة الموردين والموظفين ] ---
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
    if not vendor_data:
        staff_member = models.VendorStaff.query.filter_by(username=session.get('username')).first()
        vendor_data = staff_member.owner if staff_member else None

    wallet_no = "غير متوفر"
    balance = 0.0
    if vendor_data and vendor_data.wallet:
        wallet_no = vendor_data.wallet.wallet_number
        balance = vendor_data.wallet.balance

    show_wallet = (session.get('role') == 'vendor_owner')
    return render_template('vendor_dashboard.html', 
                           username=session.get('username'),
                           vendor=vendor_data,
                           wallet_no=wallet_no,
                           balance=balance,
                           show_wallet=show_wallet)

# --- [ بوابة الإدارة العليا - نسخة واحدة نظيفة ] ---
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

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'super_admin':
        flash("🚫 محاولة دخول غير مصرحة لبرج المراقبة!", "danger")
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard_content.html', username=session.get('username'))

# --- [ التوجيهات العامة ] ---
@app.route('/')
def index():
    return redirect(url_for('vendor_login'))

@app.route('/logout')
def logout():
    session.clear()
    flash("تم الخروج من النظام السيادي.", "info")
    return redirect(url_for('vendor_login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
