import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db
import models

# استيراد المنطق الخاص بالدخول من الملفات الخارجية
from vendor_logic import login_vendor
from admin_logic import verify_admin_credentials

app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

# --- [ منطقة السيادة: تهيئة وإعادة بناء القاعدة ] ---
with app.app_context():
    try:
        # السطور التالية تمسح وتنشئ الجداول لضمان وجود الأعمدة الجديدة (role, status)
        # ملاحظة: قم بتعطيل db.drop_all() بعد أول تشغيل ناجح للحفاظ على بياناتك
        db.drop_all() 
        db.create_all() 
        models.seed_system()
        print("✅ تم تحديث الهيكل الرقمي وحقن بيانات 'علي محجوب' بنجاح.")
    except Exception as e:
        print(f"❌ خطأ في تهيئة القاعدة: {e}")

# --- [ بوابة الموردين ] ---
@app.route('/vendor/login', methods=['GET', 'POST'])
def vendor_login():
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        success, msg = login_vendor(u, p)
        if success:
            flash(msg, "success")
            return redirect(url_for('vendor_dashboard'))
        
        flash(msg, "danger")
    
    # التعديل: استخدام الاسم الجديد للملف templates/login_vendor.html
    return render_template('login_vendor.html')

@app.route('/vendor/dashboard')
def vendor_dashboard():
    # التحقق من أن المستخدم لديه صلاحية مورد (مالك أو موظف)
    if 'role' not in session or 'vendor' not in session.get('role'):
        flash("يرجى تسجيل الدخول للوصول إلى لوحة التحكم.", "warning")
        return redirect(url_for('vendor_login'))
    
    # تحديد ظهور محفظة المورد بناءً على الدور
    show_wallet = (session.get('role') == 'vendor_owner')
    return render_template('vendor_dashboard.html', 
                           username=session.get('username'), 
                           show_wallet=show_wallet)

# --- [ بوابة الإدارة العليا: علي محجوب ] ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        # استخدام دالة التحقق من admin_logic
        success, msg = verify_admin_credentials(u, p)
        if success:
            flash(msg, "success")
            return redirect(url_for('admin_dashboard'))
        
        flash(msg, "danger")
    
    # التعديل: استخدام الاسم الجديد للملف templates/login_admin.html
    return render_template('login_admin.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    # حماية المسار للإدارة العليا فقط
    if session.get('role') != 'super_admin':
        flash("هذه المنطقة محمية للإدارة فقط.", "danger")
        return redirect(url_for('admin_login'))
    
    return render_template('admin_dashboard.html', username=session.get('username'))

# --- [ المسارات العامة والخدمات ] ---
@app.route('/')
def index():
    return redirect(url_for('vendor_login'))

@app.route('/logout')
def logout():
    session.clear()
    flash("تم تسجيل الخروج وتأمين الجلسة.", "info")
    return redirect(url_for('vendor_login'))

if __name__ == '__main__':
    # التوافق مع Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
