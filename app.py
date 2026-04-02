import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from config import Config
from database import db, init_db, Product, Vendor 
from logic import login_vendor, logout, is_logged_in
from sync_service import send_to_qumra_webhook 

app = Flask(__name__)
app.config.from_object(Config)

# ضمان وجود مسار الرفع من الإعدادات
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # إنشاء المجلد تلقائياً إذا لم يوجد

# تهيئة قاعدة البيانات (تفعيل الترقيع الذكي للأعمدة)
init_db(app)

@app.route('/')
def index():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')
        if login_vendor(user, pw):
            return redirect(url_for('dashboard'))
        flash("❌ خطأ في اسم المستخدم أو كلمة المرور", "danger")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    vendor = Vendor.query.filter_by(username=session['username']).first()
    
    try:
        # عرض منتجات المورد الحالي فقط
        products = Product.query.filter_by(vendor_username=session['username']).all()
        products_count = len(products)
    except Exception as e:
        print(f"⚠️ تنبيه أثناء جلب الإحصائيات: {e}")
        products_count = 0
        products = []
    
    return render_template('dashboard.html', vendor=vendor, products_count=products_count, products=products)

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
            flash("❌ يرجى إدخال اسم المنتج وسعره.", "danger")
            return redirect(url_for('add_product'))

        try:
            final_price = float(p_price)
            image_filename = None

            # معالجة الصورة بأمان
            if p_image and p_image.filename != '':
                # نستخدم secure_filename لحماية السيرفر
                image_filename = secure_filename(p_image.filename)
                # حفظ الصورة في المسار المحدد
                p_image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

            # الحفظ المحلي: لاحظ استخدام image_file ليتوافق مع database.py المحدث
            new_item = Product(
                name=p_name,
                price=final_price,
                description=p_desc,
                image_file=image_filename, 
                vendor_username=session['username']
            )
            
            db.session.add(new_item)
            db.session.commit()
            
            # إطلاق المزامنة السيادية عبر GraphQL
            try:
                # نرسل السعر كنص واسم الصورة للربط الخارجي
                status = send_to_qumra_webhook(p_name, str(final_price), p_desc, image_filename)
                if status:
                    flash(f"🚀 تم رفع {p_name} ومزامنته مع المتجر بنجاح!", "success")
                else:
                    flash(f"✅ تم الحفظ في لوحتك، جاري تحديث بيانات المتجر الخارجي.", "info")
            except Exception as sync_err:
                print(f"📡 خطأ مزامنة خارجية: {sync_err}")
                flash(f"⚠️ المنتج متاح في لوحتك، سيتم مزامنته لاحقاً.", "warning")

            return redirect(url_for('dashboard'))

        except ValueError:
            flash("❌ خطأ: السعر يجب أن يكون رقماً.", "danger")
        except Exception as e:
            db.session.rollback()
            print(f"❌ خطأ قاعدة بيانات: {e}")
            flash(f"❌ حدث خطأ فني أثناء الحفظ المحلي.", "danger")
            return redirect(url_for('dashboard'))

    return render_template('add_product.html')

@app.route('/webhook/qumra', methods=['POST'])
def qumra_receiver():
    """استقبال تحديثات الطلبات من قمرة"""
    try:
        data = request.json
        print(f"📡 إشارة قادمة من قمرة: {data}")
        return {"status": "success", "message": "Mahjoub Received"}, 200
    except Exception as e:
        print(f"❌ خطأ ويب هوك: {e}")
        return {"status": "error"}, 400

@app.route('/logout')
def logout_route():
    return logout()

if __name__ == '__main__':
    # دعم بورت Railway التلقائي
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
