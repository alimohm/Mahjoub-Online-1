import os
import requests  # ضروري لإرسال البيانات للمتجر عبر الأدوات
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db, init_db, Vendor
import logic

app = Flask(__name__)

# مفتاح التشفير للجلسات (يفضل وضعه في Variables في ريلوي)
app.secret_key = os.environ.get('SECRET_KEY', 'mahjoub_sovereign_2026_key')

# المفتاح الأخير لربط المتجر (API Key)
MAHJOUB_API_KEY = "qmr_dcbbd1f6-d0a7-43ed-9b4c-4a9394be06b9"
STORE_URL = "https://mahjoub.online/api/v1/products" # رابط الأدوات الافتراضي

# تهيئة قاعدة البيانات Postgres
init_db(app)

@app.route('/')
def index():
    if 'vendor_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'vendor_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        
        # المنطق الذي يفرق بين (غير مسجل) و (كلمة مرور خطأ)
        vendor, message = logic.perform_login(u, p)
        
        if vendor:
            session['vendor_id'] = vendor.id
            session['vendor_name'] = vendor.owner_name or vendor.username
            return redirect(url_for('dashboard'))
        else:
            flash(message) # إظهار التنبيه المنطقي في الواجهة
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # حماية الهيكل من الدخول غير المصرح به
    vendor_id = session.get('vendor_id')
    if not vendor_id:
        return redirect(url_for('login'))
        
    # جلب بيانات المورد (بما فيها المحفظة التلقائية MQ)
    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        session.clear()
        return redirect(url_for('login'))
        
    return render_template('dashboard.html', vendor=vendor)

@app.route('/add_product', methods=['POST'])
def add_product():
    vendor_id = session.get('vendor_id')
    if not vendor_id:
        return redirect(url_for('login'))
    
    vendor = Vendor.query.get(vendor_id)
    
    # 1. استلام البيانات من نافذة الرفع
    product_name = request.form.get('name')
    product_price = request.form.get('price')
    product_desc = request.form.get('description')
    
    # 2. تجهيز البيانات للإرسال عبر الأدوات (API)
    payload = {
        "api_key": MAHJOUB_API_KEY,
        "vendor_wallet": vendor.wallet_address,
        "product_name": product_name,
        "price": product_price,
        "description": product_desc
    }
    
    try:
        # 3. النشر الفعلي في متجر محجوب أونلاين
        # ملاحظة: تم استخدام POST لإرسال البيانات للأدوات
        response = requests.post(STORE_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            flash(f"تم نشر المنتج '{product_name}' بنجاح عبر محفظتك {vendor.wallet_address}")
        else:
            # في حال فشل الربط التقني
            flash("فشل النشر: تأكد من صلاحية مفتاح الربط (API Key)")
            
    except Exception as e:
        flash("حدث خطأ أثناء الاتصال بالمتجر، جرب مرة أخرى")

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    # التوافق مع إعدادات Railway لفتح المنفذ الصحيح
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
