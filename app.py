import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# مفتاح الأمان ضروري لعمل الجلسات (Sessions)
app.secret_key = os.environ.get('SECRET_KEY', 'mahjoub_online_2026')

# --- إعداد قاعدة بيانات Railway ---
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- نماذج البيانات الموحدة ---
class Vendor(db.Model):
    __tablename__ = 'vendor'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    owner_name = db.Column(db.String(100))
    wallet_address = db.Column(db.String(100))

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))

# --- المسارات ---
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        vendor = Vendor.query.filter_by(username=u, password=p).first()
        if vendor:
            session['vendor_id'] = vendor.id
            session['vendor_name'] = vendor.owner_name
            session['wallet'] = vendor.wallet_address
            return redirect(url_for('dashboard'))
        flash("خطأ في اسم المستخدم أو كلمة المرور")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    # جلب المنتجات لتمريرها للقالب
    products = Product.query.filter_by(vendor_id=session['vendor_id']).all()
    return render_template('dashboard.html', products=products)

@app.route('/upload_product', methods=['POST'])
def upload_product():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    
    name = request.form.get('name')
    price = request.form.get('price')
    desc = request.form.get('description')
    
    if name and price:
        new_product = Product(name=name, price=float(price), description=desc, vendor_id=session['vendor_id'])
        db.session.add(new_product)
        db.session.commit()
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
