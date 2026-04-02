import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

from config import Config
from database import db, init_db
from models import Product, Vendor
from logic import login_vendor, logout, is_logged_in
from sync_service import send_to_qumra_webhook

app = Flask(__name__)
app.config.from_object(Config)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# تهيئة القاعدة (PostgreSQL)
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
        user_input = request.form.get('username')
        pass_input = request.form.get('password')
        
        # استدعاء دالة التحقق من قاعدة البيانات
        if login_vendor(user_input, pass_input):
            return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    user_session = session.get('username')
    vendor = Vendor.query.filter_by(username=user_session).first()
    products = Product.query.filter_by(vendor_username=user_session, is_published=False).all()
    
    return render_template('dashboard.html', vendor=vendor, products=products)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    if request.method == 'GET':
        return render_template('add_product.html')
    
    p_name = request.form.get('name')
    p_price = request.form.get('price')
    p_desc = request.form.get('description', '')
    p_image = request.files.get('image')

    if p_name and p_price:
        try:
            image_filename = None
            if p_image and p_image.filename != '':
                ext = os.path.splitext(p_image.filename)[1]
                image_filename = f"{secure_filename(p_name)}_{os.urandom(2).hex()}{ext}"
                p_image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

            new_item = Product(
                name=p_name,
                price=float(p_price),
                description=p_desc,
                image_file=image_filename,
                vendor_username=session['username']
            )
            db.session.add(new_item)
            db.session.commit()

            # مزامنة قمرة
            success = send_to_qumra_webhook(p_name, p_price, p_desc, image_filename)
            
            if success:
                new_item.is_published = True
                db.session.commit()
                flash(f"✅ تم رفع {p_name} بنجاح!", "success")
            else:
                flash(f"⚠️ حفظ محلي، فشل الإرسال لقمرة.", "warning")

            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f"❌ خطأ: {str(e)}", "danger")

    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout_route():
    return logout()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
