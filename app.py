import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# استيراد إعدادات المشروع والبنية التحتية
from config import Config
from database import db, init_db
from models import Product, Vendor
from logic import login_vendor, logout, is_logged_in
from sync_service import send_to_qumra_webhook

app = Flask(__name__)
app.config.from_object(Config)

# إعدادات رفع الملفات (Media) لضمان حفظ صور المنتجات
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# تهيئة قاعدة البيانات اللامركزية (PostgreSQL/Postgres)
init_db(app)

# --- المسارات والروابط البرمجية (Routes) ---

@app.route('/')
def index():
    """توجيه المستخدم حسب حالة تسجيل الدخول لضمان الانسيابية"""
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """صفحة الدخول: بوابة العبور لـ سوقك الذكي"""
    if is_logged_in():
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        user_input = request.form.get('username')
        pass_input = request.form.get('password')
        
        # التحقق من الهوية اللامركزية في قاعدة البيانات
        if login_vendor(user_input, pass_input):
            flash("مرحباً بك في عالم محجوب أونلاين اللامركزي 🚀", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("خطأ في بيانات الدخول، يرجى المحاولة مرة أخرى.", "danger")
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """لوحة التحكم: المحرك الذي يستدعي الهيكل (layout) ويعرض إحصائيات المورد"""
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    user_session = session.get('username')
    
    # استدعاء بيانات المورد (الاسم، البراند، المحفظة) لظهورها في الهيكل (layout.html)
    vendor_data = Vendor.query.filter_by(username=user_session).first()
    
    # استدعاء المنتجات المحلية المربوطة بهذا التاجر لعرضها في جدول (dashboard.html)
    # نركز على المنتجات التي لم تنشر بعد (is_published=False) لسهولة الإدارة
    products_list = Product.query.filter_by(vendor_username=user_session, is_published=False).all()
    
    # تمرير البيانات للقالب (التمرير الصحيح يضمن ظهور الهيكل والداشبورد معاً)
    return render_template('dashboard.html', vendor=vendor_data, products=products_list)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    """إضافة منتج: الربط مع الذكاء الاصطناعي وهوية التاجر اللامركزية"""
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    user_session = session.get('username')
    vendor = Vendor.query.filter_by(username=user_session).first()

    if request.method == 'GET':
        # تمرير بيانات التاجر لضمان ظهور برانده ومحفظته في الهيكل أثناء الإضافة
        return render_template('add_product.html', vendor=vendor)
    
    # استلام البيانات من فورم "سوقك الذكي" الاحترافي
    p_name = request.form.get('name')
    p_price = request.form.get('price')
    p_currency = request.form.get('currency', 'YER')
    p_stock = request.form.get('stock', 1)
    p_desc = request.form.get('description', '') # الوصف المنسق والمدعوم بالإيموجيات
    p_image = request.files.get('image')

    if p_name and p_price:
        try:
            # معالجة وحفظ صورة المنتج باسم احترافي لـ SEO
            image_filename = None
            if p_image and p_image.filename != '':
                ext = os.path.splitext(p_image.filename)[1]
                image_filename = f"{secure_filename(p_name)}_{os.urandom(2).hex()}{ext}"
                p_image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

            # إنشاء المنتج وربطه آلياً بالعلامة التجارية المسجلة للمورد في "القاعجة"
            new_product = Product(
                name=p_name,
                brand=vendor.brand_name, # الربط المباشر ببراند التاجر
                price=float(p_price),
                currency=p_currency,
                stock=int(p_stock),
                description=p_desc,
                image_file=image_filename,
                vendor_id=vendor.id,
                vendor_username=user_session
            )
            
            db.session.add(new_product)
            db.session.commit()

            # مزامنة البيانات مع المنصات الخارجية (Webhook Sync)
            # نرسل الهوية الكاملة: محجوب أونلاين - المنصة اللامركزية الأولى في اليمن
            sync_status = send_to_qumra_webhook(
                name=p_name, 
                price=p_price, 
                desc=p_desc, 
                image=image_filename,
                brand=vendor.brand_name,
                platform="محجوب أونلاين - المنصة اللامركزية الأولى في اليمن"
            )
            
            if sync_status:
                new_product.is_published = True
                db.session.commit()
                flash(f"✅ تم نشر '{p_name}' بنجاح في سوقك الذكي!", "success")
            else:
                flash(f"⚠️ حُفظ المنتج محلياً، فشل الربط الخارجي حالياً.", "warning")

            return redirect(url_for('dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f"❌ خطأ تقني: {str(e)}", "danger")

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout_route():
    """إنهاء الجلسة والخروج الآمن"""
    return logout()

# تشغيل التطبيق بما يتناسب مع بيئات الـ Production
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
