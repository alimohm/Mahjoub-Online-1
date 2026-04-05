import os
import random
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db
import models

# استدعاء المنطق البرمجي (تأكد من وجود هذه الملفات في المستودع)
from vendor_logic import login_vendor 
from admin_logic import verify_admin_credentials

app = Flask(__name__)
app.config.from_object(Config)

# تهيئة قاعدة البيانات
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
    if 'role' in session:
        if session['role'] == 'super_admin':
            return redirect(url_for('admin_dashboard'))
        elif session['role'] in ['vendor_owner', 'vendor_staff']:
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
            session.clear()
            session.permanent = True
            session['username'] = u
            session['role'] = 'super_admin'
            flash("تم الدخول لبرج المراقبة بنجاح 🛡️", "success")
            return redirect(url_for('admin_dashboard'))
        flash(msg, "danger")
    return render_template('login_admin.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'super_admin':
        flash("🚫 صلاحيات غير كافية للوصول لبرج المراقبة", "danger")
        return redirect(url_for('admin_login'))
    
    all_vendors = models.Vendor.query.all()
    # يتم استدعاء القالب الذي يرث من admin_layout.html
    return render_template('admin_dashboard.html', 
                           username=session.get('username'), 
                           vendors=all_vendors)

@app.route('/admin/create-vendor', methods=['POST'])
def create_vendor():
    if session.get('role') != 'super_admin': return redirect(url_for('admin_login'))
    
    u = request.form.get('username', '').strip()
    b = request.form.get('brand_name', '').strip()
    p = request.form.get('password', '').strip()

    if models.Vendor.query.filter_by(username=u).first():
        flash("⚠️ اسم المستخدم موجود مسبقاً.", "warning")
    else:
        try:
            new_v = models.Vendor(username=u, brand_name=b, password=p)
            db.session.add(new_v)
            db.session.flush() 

            wallet_num = f"MAH-{random.randint(100,999)}-{random.randint(1000,9999)}"
            new_wallet = models.Wallet(wallet_number=wallet_num, balance=0.0, vendor_id=new_v.id)
            db.session.add(new_wallet)
            
            db.session.commit()
            flash(f"✅ تم اعتماد المورد '{b}' بنجاح.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"❌ فشل الاعتماد: {str(e)}", "danger")
            
    return redirect(url_for('admin_dashboard'))

# --- [ بوابة الموردين: سوقك الذكي ] ---

@app.route('/vendor/login', methods=['GET', 'POST'])
def vendor_login():
    if 'role' in session and session.get('role') in ['vendor_owner', 'vendor_staff']:
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
    if 'role' not in session or session.get('role') not in ['vendor_owner', 'vendor_staff']:
        return redirect(url_for('vendor_login'))
    
    vendor_data = models.Vendor.query.filter_by(username=session.get('username')).first()
    
    # استخراج بيانات المحفظة لعرضها في القالب الذي يرث من vendor_layout.html
    wallet_no = vendor_data.wallet.wallet_number if vendor_data and vendor_data.wallet else "MAH-000-0000"
    balance = vendor_data.wallet.balance if vendor_data and vendor_data.wallet else 0.0
    
    return render_template('vendor_dashboard.html', 
                           username=session.get('username'),
                           vendor=vendor_data,
                           wallet_no=wallet_no,
                           balance=balance)

# --- [ نظام الخروج ] ---

@app.route('/logout')
def logout():
    role = session.get('role')
    session.clear()
    flash("تم تسجيل الخروج بنجاح.", "info")
    if role == 'super_admin':
        return redirect(url_for('admin_login'))
    return redirect(url_for('vendor_login'))

if __name__ == '__main__':
    # تشغيل السيرفر مع تفعيل Debug لمراقبة الأخطاء في Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)



@app.route('/vendor/dashboard')
def vendor_dashboard():
    # حماية المسار
    if 'role' not in session or session.get('role') not in ['vendor_owner', 'vendor_staff']:
        return redirect(url_for('vendor_login'))
    
    # جلب بيانات المورد ومحفظته
    vendor_data = models.Vendor.query.filter_by(username=session.get('username')).first()
    
    # إذا لم تكن المحفظة موجودة، نضع قيم افتراضية لمنع الخطأ
    wallet_no = vendor_data.wallet.wallet_number if vendor_data.wallet else "جاري الربط..."
    balance = vendor_data.wallet.balance if vendor_data.wallet else 0.0
    
    return render_template('vendor_dashboard.html', 
                           wallet_no=wallet_no, 
                           balance=balance)
