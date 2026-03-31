import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# الاستدعاءات
from database import db, init_db, Vendor, Product
from config import Config
import finance
import bridge_logic

app = Flask(__name__)
app.config.from_object(Config)

# إنشاء مجلد الصور
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

init_db(app)

# دالة لإنشاء بيانات أولية (لتجنب خطأ 500 عند أول تشغيل)
def create_initial_data():
    if not Vendor.query.first():
        test_vendor = Vendor(
            username="ali", 
            password="123", 
            owner_name="Ali Mahjoub"
        )
        db.session.add(test_vendor)
        db.session.commit()

@app.route('/')
def index():
    if 'vendor_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Vendor.query.filter_by(username=request.form.get('username')).first()
        if user and user.password == request.form.get('password'):
            session['vendor_id'] = user.id
            return redirect(url_for('dashboard'))
        flash("خطأ في البيانات")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    v_id = session.get('vendor_id')
    if not v_id: return redirect(url_for('login'))
    vendor = Vendor.query.get(v_id)
    return render_template('dashboard.html', vendor=vendor)

@app.route('/add_product', methods=['POST'])
def add_product():
    v_id = session.get('vendor_id')
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

    # إرسال للمتجر
    bridge_logic.push_to_store({
        "name": new_p.name, 
        "final_price": f_price, 
        "description": new_p.description, 
        "image_url": image_url, 
        "wallet": vendor.wallet_address
    })
    
    flash("تم الرفع بنجاح")
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_initial_data() # إنشاء المستخدم "ali" تلقائياً
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
