import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db, init_db, Vendor

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'mahjoub_king_2026')

# تهيئة قاعدة البيانات في ريلوي
init_db(app)

@app.route('/')
def index():
    if 'vendor_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        # التحقق الحقيقي من قاعدة البيانات
        vendor = Vendor.query.filter_by(username=u, password=p).first()
        if vendor:
            session['vendor_id'] = vendor.id
            return redirect(url_for('dashboard'))
        flash("بيانات الدخول غير صحيحة")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    vendor_id = session.get('vendor_id')
    if not vendor_id:
        return redirect(url_for('login'))
    
    # جلب بيانات المورد لملء الهيكل
    vendor = Vendor.query.get(vendor_id)
    return render_template('dashboard.html', vendor=vendor)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
