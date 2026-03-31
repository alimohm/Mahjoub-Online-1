import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db, init_db
import logic
import bridge_logic 

app = Flask(__name__)
# استخدام مفتاح سري قوي لضمان أمان الجلسات في محجوب أونلاين
app.secret_key = os.environ.get('SECRET_KEY', 'mahjoub_king_2026')

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
        vendor_obj, message = logic.perform_login(u, p)
        if vendor_obj:
            session['vendor_id'] = vendor_obj.id
            return redirect(url_for('dashboard'))
        else:
            flash(message)
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    vendor_id = session.get('vendor_id')
    vendor = logic.get_current_vendor(vendor_id)
    if not vendor:
        return redirect(url_for('login'))
    return render_template('dashboard.html', vendor=vendor)

# --- معالجة رفع المنتجات مع نظام كشف الأخطاء ---
@app.route('/add_product', methods=['POST'])
def add_product():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))

    try:
        p_name = request.form.get('name')
        p_desc = request.form.get('description')
        p_price = request.form.get('price')
        p_currency = request.form.get('currency') 
        p_image = request.files.get('image')

        # التأكد من وجود البيانات الأساسية
        if not (p_name and p_price and p_image):
            flash("يرجى إكمال جميع الحقول ورفع صورة المنتج.")
            return redirect(url_for('dashboard'))

        # 1. تحويل السعر (الحوكمة الرقمية)
        final_sar_price = bridge_logic.calculate_final_price(p_price, p_currency)

        # 2. معالجة الصورة
        processed_img = bridge_logic.process_product_image(p_image)
        
        if not processed_img:
            flash("فشلت معالجة الصورة، تأكد من جودة الملف المرفوع.")
            return redirect(url_for('dashboard'))

        # 3. محاولة الإرسال لمتجر قمرة
        success = bridge_logic.push_to_qmr_store(p_name, p_desc, final_sar_price, processed_img)

        if success:
            flash("تم رفع المنتج بنجاح! سيظهر في المتجر بعد المراجعة.")
        else:
            flash("فشل الربط التقني مع قمرة، تحقق من الـ API Key والرابط.")

    except Exception as e:
        # طباعة الخطأ الحقيقي في سجلات Railway لمعرفته فوراً
        print(f"خطأ برمجى في محجوب أونلاين: {str(e)}")
        flash(f"عذراً، حدث خطأ داخلي: {str(e)}")

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
