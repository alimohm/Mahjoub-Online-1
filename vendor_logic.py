import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db

# استيراد النماذج (Models)
import models

# استيراد منطق الأعمال (Logic)
from vendor_logic import login_vendor
from admin_logic import verify_admin_credentials

app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

# --- [ منطقة السيادة: تهيئة البنية التحتية ] ---
with app.app_context():
    try:
        # ملاحظة: قم بتعطيل db.drop_all() بعد أول تشغيل ناجح للحفاظ على بياناتك
        db.drop_all() 
        db.create_all() 
        models.seed_system()
        print("✅ تم تطهير قاعدة البيانات وبناء الهيكل الجديد وحقن البيانات بنجاح.")
    except Exception as e:
        print(f"❌ خطأ في تهيئة القاعدة: {e}")

# --- [ المسارات العامة ] ---
@app.route('/')
def index():
    return redirect(url_for('vendor_login'))

# --- [ بوابة الموردين والموظفين ] ---
@app.route('/vendor/login', methods=['GET', 'POST'])
def vendor_login():
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        success, msg = login_vendor(u, p)
        if success:
            flash(msg, "success")
            # التوجيه الصارم لدشبورد المورد
            return redirect(url_for('vendor_dashboard'))
        
        flash(msg, "danger")
    return render_template('vendor_login.html')

@app.route('/vendor/dashboard')
def vendor_dashboard():
    # حماية المسار: يجب أن يكون الدور يحتوي على 'vendor'
    if 'role' not in session or 'vendor' not in session.get('role'):
        flash("يرجى تسجيل الدخول للوصول إلى لوحة الموردين.", "warning")
        return redirect(url_for('vendor_login'))
    
    # تحديد صلاحية رؤية المحفظة (للمالك فقط)
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
        
        # استخدام المنطق من admin_logic
        success, msg = verify_admin_credentials(u, p)
        if success:
            flash(msg, "success")
            return redirect(url_for('admin_dashboard'))
        
        flash(msg, "danger")
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    # حماية المسار: لمدير النظام فقط
    if session.get('role') != 'super_admin':
        flash("هذه المنطقة مخصصة للإدارة العليا فقط.", "danger")
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html', username=session.get('username'))

# --- [ مسارات إضافية للمنتجات ] ---
@app.route('/vendor/add-product')
def add_product():
    if 'role' not in session:
        return redirect(url_for('vendor_login'))
    return render_template('vendor_add_product.html')

# --- [ الخروج وتأمين الجلسة ] ---
@app.route('/logout')
def logout():
    session.clear()
    flash("تم تسجيل الخروج بنجاح.", "info")
    return redirect(url_for('vendor_login'))

# --- [ إقلاع المحرك ] ---
if __name__ == '__main__':
    # التوافق مع بيئة Railway المتغيرة
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
