import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db, Product, Vendor 
from logic import login_vendor, logout, is_logged_in
from sync_service import send_to_qumra_webhook 

app = Flask(__name__)
app.config.from_object(Config)

# تهيئة قاعدة البيانات والربط مع Railway
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
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """لوحة التحكم - عرض الإحصائيات مع حماية من أخطاء قاعدة البيانات"""
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    # جلب بيانات المورد الحالي
    vendor = Vendor.query.filter_by(username=session['username']).first()
    
    # محاولة جلب عدد المنتجات مع حماية في حال عدم وجود عمود vendor_username
    try:
        products_count = Product.query.filter_by(vendor_username=session['username']).count()
    except Exception as e:
        print(f"⚠️ تنبيه: عمود المورد مفقود، يتم جلب العدد الكلي. الخطأ: {e}")
        try:
            products_count = Product.query.count()
        except:
            products_count = 0
    
    return render_template('dashboard.html', vendor=vendor, products_count=products_count)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    """إضافة منتج جديد - الحفظ المحلي ثم المزامنة الخارجية"""
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    if request.method == 'POST':
        # 1. سحب البيانات مع التحقق من وجودها (منع خطأ NoneType)
        p_name = request.form.get('name')
        p_price = request.form.get('price')
        p_desc = request.form.get('description', '') 
        
        if not p_name or not p_price:
            flash("❌ يرجى إدخال اسم المنتج وسعره بشكل صحيح.", "danger")
            return redirect(url_for('add_product'))

        try:
            # تحويل السعر لرقم عشري
            final_price = float(p_price)

            # 2. إنشاء كائن المنتج والحفظ المحلي
            new_item = Product(
                name=p_name,
                price=final_price,
                description=p_desc
            )
            
            # محاولة ربط المنتج بالمورد إذا كان العمود متاحاً
            try:
                if hasattr(Product, 'vendor_username'):
                    new_item.vendor_username = session['username']
            except:
                pass
                
            db.session.add(new_item)
            db.session.commit()
            
            # 3. المزامنة الخارجية (بعد نجاح الحفظ المحلي لضمان عدم ضياع البيانات)
            try:
                # نرسل السعر كنص للمزامنة الخارجية
                status = send_to_qumra_webhook(p_name, str(final_price), p_desc)
                if status:
                    flash(f"✅ تم حفظ ومزامنة {p_name} بنجاح!", "success")
                else:
                    flash(f"⚠️ تم الحفظ في لوحة محجوب، لكن فشلت المزامنة مع متجر قمرة.", "warning")
            except Exception as sync_err:
                print(f"📡 خطأ في المزامنة (Timeout): {sync_err}")
                flash(f"⚠️ المنتج متاح في لوحتك، لكن مزامنة المتجر الخارجي استغرقت وقتاً طويلاً.", "info")

        except ValueError:
            flash("❌ خطأ: السعر يجب أن يكون رقماً صحيحاً.", "danger")
        except Exception as e:
            db.session.rollback()
            print(f"❌ خطأ فني أثناء الحفظ: {e}")
            flash(f"❌ حدث خطأ فني أثناء معالجة الطلب.", "danger")
            
        return redirect(url_for('dashboard'))

    return render_template('add_product.html')

@app.route('/webhook/qumra', methods=['POST'])
def qumra_receiver():
    """استقبال التنبيهات من منصة قمرة لتحديث الرصيد والطلبات"""
    try:
        data = request.json
        print(f"📡 إشارة قادمة من قمرة: {data}")
        # هنا سيتم إضافة منطق تحديث رصيد MAH لاحقاً
        return {"status": "received"}, 200
    except:
        return {"status": "error"}, 400

@app.route('/logout')
def logout_route():
    return logout()

if __name__ == '__main__':
    # تشغيل السيرفر على المنفذ المخصص من Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
