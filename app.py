import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db, init_db
import logic
import bridge_logic  # الجسر المحدث الذي يحتوي على المفتاح الجديد

app = Flask(__name__)

# استخدام مفتاح سري قوي لتأمين جلسات الموردين في منصة محجوب أونلاين
app.secret_key = os.environ.get('SECRET_KEY', 'mahjoub_king_2026_sovereign')

# تهيئة قاعدة البيانات المحلية للموردين
init_db(app)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'vendor_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        
        # التحقق من بيانات المورد عبر ملف logic
        vendor_obj, message = logic.perform_login(u, p)
        
        if vendor_obj:
            session['vendor_id'] = vendor_obj.id
            print(f"✅ تسجيل دخول ناجح للمورد: {u}")
            return redirect(url_for('dashboard'))
        else:
            flash(message)
            print(f"⚠️ محاولة دخول فاشلة للمستخدم: {u}")
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    vendor_id = session.get('vendor_id')
    vendor = logic.get_current_vendor(vendor_id)
    if not vendor:
        return redirect(url_for('login'))
    return render_template('dashboard.html', vendor=vendor)

# --- محرك رفع المنتجات السيادي (Railway to mahjoub.online) ---
@app.route('/add_product', methods=['POST'])
def add_product():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))

    try:
        # استلام البيانات من نموذج الرفع
        p_name = request.form.get('name')
        p_desc = request.form.get('description')
        p_price = request.form.get('price')
        p_currency = request.form.get('currency', 'USD') # الافتراضي دولار
        p_image = request.files.get('image')

        # التحقق من اكتمال البيانات قبل بدء المعالجة
        if not (p_name and p_price and p_image):
            flash("تنبيه: يجب إدخال الاسم والسعر وصورة المنتج.")
            return redirect(url_for('dashboard'))

        print(f"🚀 بدء معالجة منتج جديد: {p_name}")

        # 1. تطبيق نظام الحوكمة الرقمية (تحويل العملة + 30% ربح)
        final_sar_price = bridge_logic.calculate_final_price(p_price, p_currency)
        print(f"💰 السعر النهائي المحتسب: {final_sar_price} SAR")

        # 2. معالجة الصورة وتحويلها لـ WebP (تتطلب Pillow في requirements.txt)
        processed_img = bridge_logic.process_product_image(p_image)
        
        if not processed_img:
            print("❌ فشل في معالجة الصورة - تأكد من تثبيت مكتبة Pillow")
            flash("خطأ في معالجة الصورة، يرجى المحاولة مرة أخرى.")
            return redirect(url_for('dashboard'))

        # 3. إرسال المنتج عبر الجسر السيادي إلى mahjoub.online
        success = bridge_logic.push_to_qmr_store(
            name=p_name, 
            description=p_desc, 
            final_price=final_sar_price, 
            image_buffer=processed_img
        )

        if success:
            flash(f"✅ تم رفع المنتج '{p_name}' بنجاح! سيظهر في متجرك كمسودة.")
            print(f"✨ المنتج '{p_name}' وصل إلى المتجر بنجاح.")
        else:
            flash("⚠️ فشل الربط مع المتجر. تأكد من صلاحيات المفتاح الجديد.")
            print("❌ فشل إرسال البيانات عبر الجسر المباشر.")

    except Exception as e:
        # طباعة تفاصيل الخطأ في سجلات Railway لمعرفته فوراً
        error_msg = f"خطأ برمجى في محجوب أونلاين: {str(e)}"
        print(error_msg)
        flash(f"عذراً، حدث عائق تقني: {str(e)}")

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    # تشغيل السيرفر على المنافذ المخصصة لـ Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
