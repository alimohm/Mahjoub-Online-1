import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash # ضروري جداً
from config import Config
from database import db, init_db
from models import Product, Vendor, AdminUser, seed_admin

app = Flask(__name__)
app.config.from_object(Config)

init_db(app)

# --- دالة التحقق (إذا أردت وضعها داخل app.py بدلاً من logic.py) ---
def login_vendor_logic(username, password):
    vendor = Vendor.query.filter_by(username=username).first()
    if not vendor:
        return False, "تنبيه: اسم المستخدم هذا غير مسجل في المنصة."
    
    if not check_password_hash(vendor.password, password):
        return False, "فشل تأمين البوابة: كلمة المرور غير صحيحة."
    
    if vendor.status == 'blocked':
        return False, "وصول مرفوض بقرار سيادي."
        
    session.clear()
    session['user_id'] = vendor.id
    session['username'] = vendor.username
    session['role'] = 'vendor'
    return True, f"أهلاً بك يا سيد {vendor.employee_name}"

# --- مسار تسجيل الدخول ---
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        # استدعاء الدالة التي عرفناها أعلاه
        success, message = login_vendor_logic(u, p)
        
        if success:
            flash(message, "success")
            return redirect(url_for('dashboard'))
        else:
            flash(message, "danger")
            
    return render_template('login.html')

# استكمال بقية المسارات (logout, dashboard, admin) كما في صورك...

if __name__ == '__main__':
    with app.app_context():
        seed_admin()
    app.run(host='0.0.0.0', port=8080)
