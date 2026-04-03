import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

# --- 1. تعريف التطبيق أولاً (لحل خطأ NameError) ---
app = Flask(__name__) #

# --- 2. استيراد المحركات بعد تعريف الـ app ---
from config import Config
from database import db, init_db
from models import Product, Vendor, AdminUser, seed_admin
from logic import login_vendor, is_logged_in # استدعاء منطقك من logic.py

app.config.from_object(Config)

# إعدادات الميديا
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- 3. تهيئة القاعدة وتحديث الهيكل ---
init_db(app)

with app.app_context():
    # هذا السطر سيقوم بإضافة الأعمدة المفقودة (status, wallet_address) آلياً
    db.create_all() #
    # حقن بيانات الإدارة (علي محجوب)
    seed_admin() #

# --- 4. المسارات السيادية (Routes) ---

@app.route('/')
def index():
    if is_logged_in(): return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

# بوابة دخول المورد
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in(): return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        if not u or not p:
            flash("يرجى إدخال اسم المستخدم وكلمة المرور", "warning")
            return redirect(url_for('login_page'))
            
        # استدعاء دالتك من ملف logic.py
        success, message = login_vendor(u, p)
        
        if success:
            flash(message, "success")
            return redirect(url_for('dashboard'))
        else:
            flash(message, "danger")
            
    return render_template('login.html') #

# لوحة تحكم المورد
@app.route('/dashboard')
def dashboard():
    if not is_logged_in(): return redirect(url_for('login_page'))
    vendor = Vendor.query.get(session.get('user_id'))
    products = Product.query.filter_by(vendor_id=vendor.id).all()
    return render_template('dashboard.html', vendor=vendor, products=products) #

# بوابة الخروج الآمن
@app.route('/logout')
def logout():
    session.clear()
    flash("تم تأمين البوابات بنجاح.", "info")
    return redirect(url_for('login_page'))

# --- 5. تشغيل المحرك ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
