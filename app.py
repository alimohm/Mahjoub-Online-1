import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# --- استدعاء الملفات المنفصلة من مجلدك ---
try:
    from database import db, init_db, Vendor, Product
    from config import Config
    import finance        # حسابات الـ 30%
    import bridge_logic   # الويب هوك والمحفظة
except ImportError as e:
    print(f"خطأ في استدعاء الملفات المنفصلة: {e}")

app = Flask(__name__)
app.config.from_object(Config)

init_db(app)

# إعداد مجلد الصور
UPLOAD_FOLDER = os.path.join('static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# تفعيل قاعدة البيانات والمستخدم الملكي فوراً
with app.app_context():
    db.create_all()
    if not Vendor.query.filter_by(username="ali").first():
        v = Vendor(username="ali", password="123", owner_name="Ali Mahjoub", wallet_address="MQ-2026-ROYAL")
        db.session.add(v)
        db.session.commit()

@app.route('/')
def home():
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
        flash("بيانات الدخول غير صحيحة")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # فتح الهيكل الداخلي المخصص للمورد
    v_id = session.get('vendor_id')
    if not v_id: return redirect(url_for('login'))
    vendor = Vendor.query.get(v_id)
    return render_template('dashboard.html', vendor=vendor)

@app.route('/add_product', methods=['POST'])
def add_product():
    # منطق رفع المنتج وحساب السعر الملكي
    v_id = session.get('vendor_id')
    vendor = Vendor.query.get(v_id)
    file = request.files.get('image')
    price = request.form.get('price')

    # استخدام الملف المنفصل finance.py
    f_price = finance.calculate_final_price(price, "USD")

    img_url = ""
    if file:
        filename = secure_filename(f"{v_id}_{file.filename}")
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        img_url = f"/static/uploads/{filename}"

    new_p = Product(name=request.form.get('name'), cost_price=float(price), 
                    final_price=f_price, image_url=img_url, vendor_id=v_id)
    db.session.add(new_p)
    db.session.commit()

    # استخدام الملف المنفصل bridge_logic.py
    bridge_logic.push_to_store({"name": new_p.name, "price": f_price, "wallet": vendor.wallet_address})
    
    flash("تم النشر وتحديث بيانات المحفظة!")
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
