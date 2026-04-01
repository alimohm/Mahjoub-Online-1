import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db, Product, Vendor 
from logic import login_vendor, logout, is_logged_in
from sync_service import send_to_qumra_webhook 

app = Flask(__name__)
app.config.from_object(Config)

# تهيئة قاعدة البيانات والربط مع Railway مع التحديث التلقائي للأعمدة
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
    """لوحة التحكم - عرض الإحصائيات مع الخصوصية لكل مورد"""
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    # جلب بيانات المورد الحالي
    vendor = Vendor.query.filter_by(username=session['username']).first()
    
    # جلب عدد المنتجات الخاصة بهذا المورد فقط (بناءً على التحديث الجديد للقاعدة)
    try:
        products_count = Product.query.filter_by(vendor_username=session['username']).count()
    except Exception as e:
        print(f"⚠️ تنبيه أثناء جلب الإحصائيات: {e}")
        products_count = 0
    
    return render_template('dashboard.html', vendor=vendor, products_count=products_count)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    """إضافة منتج جديد - الحفظ المحلي السريع ثم محاولة المزامنة"""
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    if request.method == 'POST':
        # 1. سحب البيانات والتحقق الأولي
        p_name = request.form.get('name')
        p_price = request.form.get('price')
        p_desc = request.form.get('description', '') 
        
        if not p_name or not p_price:
            flash("❌ يرجى إدخال اسم المنتج وسعره.", "danger")
            return redirect(url_for('add_product'))

        try:
            final_price = float(p_price)

            # 2. الحفظ المحلي الفوري (لضمان بقاء البيانات في محجوب أونلاين)
            new_item = Product(
                name=p_name,
                price=final_price,
                description=p_desc,
                vendor_username=session['username']
            )
            
            db.session.add(new_item)
            db.session.commit()
            
            # فلاش سريع للمستخدم بنجاح الحفظ المحلي
            flash(f"✅ تم تسجيل المنتج {p_name} في نظام محجوب بنجاح.", "success")

            # 3. المزامنة الخارجية مع قمرة (في بلوك مستقل لتجنب تعليق الطلب)
            try:
                # نستخدم timeout قصير داخل send_to_qumra_webhook
                status = send_to_qumra_webhook(p_name, str(final_price), p_desc)
                if status:
                    print(f"✅ تم مزامنة {p_name} مع متجر قمرة بنجاح.")
                else:
                    print(f"⚠️ فشلت المزامنة التلقائية مع قمرة لمنتج: {p_name}")
            except Exception as sync_err:
                print(f"📡 خطأ تقني في المزامنة الخارجية: {sync_err}")

            return redirect(url_for('dashboard'))

        except ValueError:
            flash("❌ خطأ: السعر يجب أن يكون رقماً صحيحاً.", "danger")
        except Exception as e:
            db.session.rollback()
            print(f"❌ خطأ قاعدة بيانات: {e}")
            flash(f"❌ حدث خطأ فني أثناء الحفظ المحلي.", "danger")
            return redirect(url_for('dashboard'))

    return render_template('add_product.html')

@app.route('/webhook/qumra', methods=['POST'])
def qumra_receiver():
    """استقبال التنبيهات من منصة قمرة لتحديث الرصيد والطلبات"""
    try:
        data = request.json
        print(f"📡 إشارة قادمة من قمرة: {data}")
        return {"status": "received"}, 200
    except:
        return {"status": "error"}, 400

@app.route('/logout')
def logout_route():
    return logout()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
