import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# استيراد إعداداتك ومكتباتك الخاصة
from config import Config
from database import db, init_db, Product, Vendor 
from logic import login_vendor, logout, is_logged_in
from sync_service import send_to_qumra_webhook 

app = Flask(__name__)
app.config.from_object(Config)

# إعدادات المجلدات والرفع
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # حد أقصى 16 ميجا للرفع
os.makedirs(UPLOAD_FOLDER, exist_ok=True) 

# تهيئة قاعدة البيانات عند الإقلاع
init_db(app)

# 1. المسار الرئيسي: توجيه ذكي حسب حالة الدخول
@app.route('/')
def index():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

# 2. بوابة الدخول: رابط مستقل تماماً
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')
        if login_vendor(user, pw):
            # تعيين محفظة افتراضية في الجلسة إذا لم تكن موجودة
            session['wallet'] = session.get('wallet', "0xMAH_BLOCKCHAIN_IDENTITY_2026")
            return redirect(url_for('dashboard'))
        flash("❌ خطأ في اسم المستخدم أو كلمة المرور", "danger")
    
    return render_template('login.html')

# 3. لوحة التحكم (الداشبورد): استدعاء البيانات والإحصائيات
@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    # جلب بيانات المورد الحالي
    vendor = Vendor.query.filter_by(username=session['username']).first()
    
    try:
        # جلب المنتجات لحساب العدد وعرضها
        products = Product.query.filter_by(vendor_username=session['username']).all()
        products_count = len(products)
    except Exception as e:
        print(f"⚠️ تنبيه في قاعدة البيانات: {e}")
        products_count = 0
        products = []
    
    return render_template('dashboard.html', 
                           vendor=vendor, 
                           products_count=products_count, 
                           products=products)

# 4. إضافة منتج: رابط مستقل (GET للعرض و POST للحفظ)
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    if request.method == 'POST':
        p_name = request.form.get('name')
        p_price = request.form.get('price')
        p_desc = request.form.get('description', '') 
        p_image = request.files.get('image')

        if not p_name or not p_price:
            flash("❌ يرجى إكمال الحقول الأساسية.", "danger")
            return redirect(url_for('add_product'))

        try:
            final_price = float(p_price)
            image_filename = None

            # معالجة الصورة وإعادة تسميتها باسم المنتج (احترافي)
            if p_image and p_image.filename != '':
                ext = os.path.splitext(p_image.filename)[1]
                image_filename = f"{secure_filename(p_name).replace(' ', '_')}{ext}"
                p_image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

            # الحفظ في قاعدة البيانات المحلية
            new_item = Product(
                name=p_name,
                price=final_price,
                description=p_desc,
                image_file=image_filename, 
                vendor_username=session['username']
            )
            
            db.session.add(new_item)
            db.session.commit()
            
            # محاولة المزامنة الخارجية (قمرة/ويب هوك)
            try:
                send_to_qumra_webhook(p_name, str(final_price), p_desc, image_filename)
                flash(f"🚀 تم رفع {p_name} بنجاح ومزامنته!", "success")
            except:
                flash(f"✅ تم الحفظ في لوحتك، المزامنة الخارجية قيد المعالجة.", "info")

            return redirect(url_for('dashboard'))

        except Exception as e:
            db.session.rollback()
            print(f"❌ خطأ برمي: {e}")
            flash("❌ حدث خطأ فني أثناء الرفع.", "danger")
            return redirect(url_for('add_product'))

    # فتح صفحة الإضافة عند طلب الرابط (GET)
    return render_template('add_product.html')

# 5. تسجيل الخروج
@app.route('/logout')
def logout_route():
    return logout()

# تشغيل السيرفر ودعم Railway
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
