import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db, Product, Vendor 
from logic import login_vendor, logout, is_logged_in
from sync_service import send_to_qumra_webhook 

app = Flask(__name__)
app.config.from_object(Config)

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
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    vendor = Vendor.query.filter_by(username=session['username']).first()
    
    try:
        products_count = Product.query.filter_by(vendor_username=session['username']).count()
    except Exception as e:
        print(f"⚠️ تنبيه: عمود المورد مفقود: {e}")
        try:
            products_count = Product.query.count()
        except:
            products_count = 0
    
    return render_template('dashboard.html', vendor=vendor, products_count=products_count)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    if request.method == 'POST':
        # 1. سحب البيانات بأمان مع حماية من القيم الفارغة (حل خطأ NoneType)
        p_name = request.form.get('name')
        p_price = request.form.get('price')
        p_desc = request.form.get('description', '') # وصف اختياري
        
        if not p_name or not p_price:
            flash("❌ يرجى إدخال اسم المنتج وسعره.", "danger")
            return redirect(url_for('add_product'))

        try:
            # تحويل السعر مع معالجة الأخطاء
            final_price = float(p_price)

            # 2. التثبيت المحلي الفوري
            new_item = Product(
                name=p_name,
                price=final_price,
                description=p_desc
            )
            
            # محاولة ربط المورد إذا كان الحقل موجوداً في قاعدة البيانات
            try:
                new_item.vendor_username = session['username']
            except:
                pass
                
            db.session.add(new_item)
            db.session.commit()
            
            # 3. المزامنة مع قمرة (مع وضع حد للانتظار لتجنب WORKER TIMEOUT)
            # المزامنة تتم الآن بعد أن ضمنا حفظ البيانات محلياً
            try:
                status = send_to_qumra_webhook(p_name, str(final_price), p_desc)
                if status:
                    flash(f"✅ تم حفظ ومزامنة {p_name} بنجاح!", "success")
                else:
                    flash(f"⚠️ تم الحفظ محلياً، لكن فشلت المزامنة الخارجية.", "warning")
            except Exception as sync_err:
                print(f"Sync Timeout/Error: {sync_err}")
                flash(f"⚠️ المنتج متاح في لوحتك، لكن مزامنة قمرة تأخرت.", "info")

        except ValueError:
            flash("❌ خطأ: السعر يجب أن يكون رقماً.", "danger")
        except Exception as e:
            db.session.rollback()
            print(f"❌ خطأ قاعدة بيانات: {e}")
            flash(f"❌ حدث خطأ فني أثناء الحفظ.", "danger")
            
        return redirect(url_for('dashboard'))

    return render_template('add_product.html')

@app.route('/webhook/qumra', methods=['POST'])
def qumra_receiver():
    data = request.json
    print(f"📡 إشارة قادمة من قمرة: {data}")
    return {"status": "received"}, 200

@app.route('/logout')
def logout_route():
    return logout()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
