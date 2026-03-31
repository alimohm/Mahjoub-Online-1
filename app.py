import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db, init_db
import logic
import bridge_logic  # الجسر الذي يستخدم المفتاح الجديد qmr_dcbbd...

app = Flask(__name__)

# تأمين الجلسات بمفتاح سيادي (يفضل وضعه في Environment Variables في Railway)
app.secret_key = os.environ.get('SECRET_KEY', 'mahjoub_king_2026_sovereign_gold')

# تهيئة قاعدة بيانات الموردين المحلية (لوحة قمرة)
init_db(app)

@app.route('/')
def index():
    # إذا كان المورد مسجل دخوله مسبقاً، اذهب للوحة التحكم فوراً
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
        
        # التحقق من بيانات المورد عبر ملف logic
        vendor_obj, message = logic.perform_login(u, p)
        
        if vendor_obj:
            session['vendor_id'] = vendor_obj.id
            print(f"✅ دخول سيادي للمورد: {u}")
            return redirect(url_for('dashboard'))
        else:
            flash(message)
            print(f"⚠️ محاولة دخول فاشلة للمستخدم: {u}")
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    vendor_id = session.get('vendor_id')
    if not vendor_id:
        return redirect(url_for('login'))
        
    vendor = logic.get_current_vendor(vendor_id)
    if not vendor:
        session.clear()
        return redirect(url_for('login'))
        
    return render_template('dashboard.html', vendor=vendor)

# --- محرك رفع المنتجات العظيم (الربط المباشر مع mahjoub.online) ---
@app.route('/add_product', methods=['POST'])
def add_product():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))

    try:
        # استلام البيانات من واجهة قمرة (التكلفة + التفاصيل)
        p_name = request.form.get('name')
        p_desc = request.form.get('description')
        p_cost_price = request.form.get('price') # هذا سعر التكلفة من المورد
        p_currency = request.form.get('currency', 'SAR') 
        p_image = request.files.get('image')

        # التحقق من البيانات الأساسية لضمان عدم انهيار السيرفر
        if not (p_name and p_cost_price and p_image):
            flash("تنبيه: يجب إدخال الاسم والتكلفة وصورة المنتج يا عظيم.")
            return redirect(url_for('dashboard'))

        print(f"🚀 بدء معالجة منتج لـ محجوب أونلاين: {p_name}")

        # 1. الحساب الآلي (سعر التكلفة + الربح 30%) عبر الجسر
        # ملاحظة: bridge_logic سيتعامل مع تحويل العملات لضمان السعر بالـ SAR
        final_price = bridge_logic.calculate_final_price(p_cost_price, p_currency)
        print(f"💰 سعر التكلفة: {p_cost_price} | السعر النهائي للبيع: {final_price} SAR")

        # 2. معالجة الصور (WebP + SEO) لرفع أداء المتجر
        processed_img_url = bridge_logic.process_product_image(p_image)
        
        if not processed_img_url:
            print("❌ عائق في معالجة الصورة - تحقق من Pillow")
            flash("خطأ في معالجة الصورة، جرب صيغة أخرى.")
            return redirect(url_for('dashboard'))

        # 3. دفع البيانات عبر الجسر باستخدام المفتاح الجديد: qmr_dcbbd1f6...
        success, response_msg = bridge_logic.push_to_mahjoub_store(
            name=p_name, 
            description=p_desc, 
            final_price=final_price, 
            image_url=processed_img_url,
            vendor_id=session['vendor_id']
        )

        if success:
            flash(f"✨ تم نشر '{p_name}' بنجاح في سوقك الذكي!")
            print(f"✅ المنتج وصل للسيرفر الأساسي. السعر النهائي: {final_price}")
        else:
            flash(f"⚠️ عائق في الربط: {response_msg}")
            print(f"❌ فشل الإرسال: {response_msg}")

    except Exception as e:
        error_msg = f"⚠️ خطأ في app.py: {str(e)}"
        print(error_msg)
        flash("حدث عائق تقني أثناء الرفع، جاري الفحص.")

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    # التشغيل المتوافق مع منافذ Railway الديناميكية
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
