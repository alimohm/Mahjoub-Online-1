import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db, Product, Vendor # استيراد النماذج للتفاعل مع البيانات
from logic import login_vendor, logout, is_logged_in
from sync_service import send_to_qumra_webhook 

app = Flask(__name__)
app.config.from_object(Config)

# ربط المحرك بقاعدة البيانات في Railway
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
    """لوحة التحكم السيادية - عرض الإحصائيات الحقيقية"""
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    # سحب إحصائيات المورد من قاعدة البيانات لتعكس الواقع في الواجهة الأرجوانية
    vendor = Vendor.query.filter_by(username=session['username']).first()
    products_count = Product.query.filter_by(vendor_username=session['username']).count()
    
    return render_template('dashboard.html', 
                           vendor=vendor, 
                           products_count=products_count)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    if request.method == 'POST':
        p_name = request.form.get('name')
        p_price = request.form.get('price')
        p_desc = request.form.get('description')
        
        # 1. التثبيت المحلي في قاعدة بيانات محجوب أونلاين أولاً (لحل مشكلة اختفاء المنتج)
        try:
            new_item = Product(
                name=p_name,
                price=float(p_price),
                description=p_desc,
                vendor_username=session['username']
            )
            db.session.add(new_item)
            db.session.commit()
            
            # 2. المزامنة الخارجية مع متجر قمرة
            status = send_to_qumra_webhook(p_name, p_price, p_desc)
            
            if status:
                flash(f"✅ تم الرفع والمزامنة السيادية لـ {p_name}", "success")
            else:
                flash(f"⚠️ تم الحفظ محلياً ولكن فشلت المزامنة الخارجية (تحقق من الويب هوك).", "warning")
        except Exception as e:
            db.session.rollback()
            flash(f"❌ حدث خطأ فني أثناء الحفظ: {str(e)}", "danger")
            
        return redirect(url_for('dashboard'))

    return render_template('add_product.html')

# ==========================================
# قناة استقبال الإشعارات من قمرة (Webhooks)
# ==========================================
@app.route('/webhook/qumra', methods=['POST'])
def qumra_receiver():
    """استقبال نبض المتجر وتحديث الأرصدة والمنتجات تلقائياً"""
    data = request.json
    # طباعة الإشارة في Railway Logs للمراقبة
    print(f"📡 إشارة سيادية قادمة من قمرة: {data}")
    
    # مستقبلاً هنا سنضيف منطق زيادة رصيد MAH عند كل عملية بيع
    return {"status": "received"}, 200

@app.route('/logout')
def logout_route():
    return logout()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
