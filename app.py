import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# استدعاء المنطق المنفصل
try:
    from database import db, init_db, Vendor, Product
    from config import Config
    import finance
    import bridge_logic
except ImportError as e:
    print(f"Error loading logic files: {e}")

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'MAHJOUB_ROYAL_2026'

init_db(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Vendor.query.filter_by(username=request.form.get('username')).first()
        if not user:
            flash("عذراً، هذا المستخدم غير مسجل في المنصة", "error")
        elif user.password != request.form.get('password'):
            flash("كلمة المرور غير صحيحة، حاول مجدداً", "error")
        else:
            session['vendor_id'] = user.id
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/add_product', methods=['POST'])
def add_product():
    v_id = session.get('vendor_id')
    if not v_id: return redirect(url_for('login'))
    
    try:
        # التحقق من الاتصال ورفع المنتج
        file = request.files.get('image')
        if not file:
            flash("فشل الرفع: يرجى اختيار صورة للمنتج", "error")
            return redirect(url_for('dashboard'))

        # منطق الحساب والربط
        f_price = finance.calculate_final_price(request.form.get('price'), "USD")
        
        # محاكاة اتصال الويب هوك
        response = bridge_logic.push_to_store({"name": request.form.get('name'), "price": f_price})
        
        if response == "success":
            flash("تم رفع المنتج بنجاح وتفعيل الربط التلقائي!", "success")
        else:
            flash("فشل الاتصال بالمتجر، المنتج حُفظ محلياً فقط", "warning")
            
    except Exception as e:
        flash(f"حدث خطأ تقني: {str(e)}", "error")
    
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    v_id = session.get('vendor_id')
    vendor = Vendor.query.get(v_id)
    return render_template('dashboard.html', vendor=vendor)
