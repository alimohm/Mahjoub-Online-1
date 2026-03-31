import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# الاستدعاءات من الملفات المحلية
# ملاحظة: تأكد أن هذه الملفات موجودة في نفس المجلد
try:
    from database import db, init_db, Vendor, Product
    from config import Config
    import finance
    import bridge_logic
except ImportError as e:
    print(f"خطأ في استدعاء الملفات: {e}")

app = Flask(__name__)
app.config.from_object(Config)

# تأكد من تهيئة قاعدة البيانات فوراً
init_db(app)

# إنشاء مجلد الصور تلقائياً
UPLOAD_FOLDER = os.path.join('static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# دالة لإنشاء مستخدم تجريبي للدخول
def create_test_user():
    with app.app_context():
        db.create_all()
        if not Vendor.query.filter_by(username="ali").first():
            test_v = Vendor(username="ali", password="123", owner_name="Ali Mahjoub")
            db.session.add(test_v)
            db.session.commit()
            print("تم إنشاء مستخدم الدخول: ali / 123")

# --- المسارات (Routes) ---

@app.route('/')
def home():
    # إذا لم يكن مسجلاً، اذهب فوراً لصفحة الدخول
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Vendor.query.filter_by(username=request.form.get('username')).first()
        if user and user.password == request.form.get('password'):
            session['vendor_id'] = user.id
            return redirect(url_for('dashboard'))
        flash("خطأ في بيانات الدخول")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    v_id = session.get('vendor_id')
    if not v_id:
        return redirect(url_for('login'))
    vendor = Vendor.query.get(v_id)
    return render_template('dashboard.html', vendor=vendor)

@app.route('/add_product', methods=['POST'])
def add_product():
    v_id = session.get('vendor_id')
    if not v_id: return redirect(url_for('login'))
    
    vendor = Vendor.query.get(v_id)
    file = request.files.get('image')
    
    image_url = ""
    if file:
        filename = secure_filename(f"{v_id}_{file.filename}")
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        image_url = f"{request.url_root.rstrip('/')}/static/uploads/{filename}"

    f_price = finance.calculate_final_price(request.form.get('price'), request.form.get('currency'))

    new_p = Product(
        name=request.form.get('name'),
        description=request.form.get('description'),
        cost_price=float(request.form.get('price')),
        final_price=f_price,
        image_url=image_url,
        vendor_id=v_id
    )
    db.session.add(new_p)
    db.session.commit()

    bridge_logic.push_to_store({
        "name": new_p.name, 
        "final_price": f_price, 
        "description": new_p.description, 
        "image_url": image_url, 
        "wallet": vendor.wallet_address
    })
    
    flash("تم رفع المنتج بنجاح!")
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    create_test_user()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
