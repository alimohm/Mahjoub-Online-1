import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db
import models
from vendor_logic import login_vendor

app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

# --- [ منطقة السيادة وإعادة الهيكلة الرقمية ] ---
with app.app_context():
    try:
        # ملاحظة هامة: السطر القادم يضمن مزامنة الأعمدة (role, status) مع Postgres
        # أزل علامة (#) لمرة واحدة عند الرفع القادم لتطهير القاعدة
        db.drop_all() 
        db.create_all() 
        models.seed_system()
        print("✅ تم بناء البنية التحتية وحقن بيانات 'علي محجوب' بنجاح.")
    except Exception as e:
        print(f"❌ خطأ في القاعدة: {e}")

# --- [ المسارات العامة ] ---
@app.route('/')
def index():
    return redirect(url_for('vendor_login'))

# --- [ بوابة الموردين: الملاك والموظفين ] ---
@app.route('/vendor/login', methods=['GET', 'POST'])
def vendor_login():
    if request.method == 'POST':
        # استخدام .strip() لمنع أخطاء المسافات الزائدة
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        success, msg = login_vendor(u, p)
        if success:
            flash(msg, "success")
            # التوجيه الإجباري للدشبورد لضمان عدم الدخول على "أي شيء"
            return redirect(url_for('vendor_dashboard'))
        
        flash(msg, "danger")
    return render_template('vendor_login.html')

@app.route('/vendor/dashboard')
def vendor_dashboard():
    # حماية الدشبورد: التحقق من وجود دور 'vendor' في الجلسة
    if 'role' not in session or 'vendor' not in session.get('role'):
        flash("عذراً، يجب تسجيل الدخول للوصول إلى لوحة التحكم.", "warning")
        return redirect(url_for('vendor_login'))
    
    # تحديد صلاحية رؤية المحفظة المالية
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
        
        # التأكد من مطابقة البيانات المحقونة في seed_system
        if u == "علي محجوب" and p == "admin_password_123":
            session.clear() # تنظيف أي جلسة سابقة
            session['role'] = 'super_admin'
            session['username'] = u
            flash(f"مرحباً بك يا سيد علي. تم تفعيل صلاحيات الإدارة.", "success")
            return redirect(url_for('admin_dashboard'))
        
        flash("خطأ: بيانات الدخول للإدارة غير صحيحة.", "danger")
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    # حماية لوحة الإدارة العليا
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html', username=session.get('username'))

# --- [ عمليات الخروج ] ---
@app.route('/logout')
def logout():
    session.clear()
    flash("تم تسجيل الخروج وتأمين الجلسة.", "info")
    return redirect(url_for('vendor_login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
