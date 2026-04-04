import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db

app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

with app.app_context():
    import models
    # هام: قم بإلغاء التعليق عن السطر التالي لمرة واحدة فقط لمسح الخطأ القديم
    # db.drop_all() 
    db.create_all() 
    models.seed_system()

@app.route('/')
def index():
    return redirect(url_for('vendor_login'))

@app.route('/vendor/login', methods=['GET', 'POST'])
def vendor_login():
    if request.method == 'POST':
        from vendor_logic import login_vendor
        u = request.form.get('username')
        p = request.form.get('password')
        success, msg = login_vendor(u, p)
        if success: return redirect(url_for('vendor_dashboard'))
        flash(msg, "danger")
    return render_template('vendor_login.html')

@app.route('/vendor/dashboard')
def vendor_dashboard():
    if 'role' not in session: return redirect(url_for('vendor_login'))
    # عرض المحفظة فقط إذا كان المستخدم owner
    show_wallet = (session.get('role') == 'vendor_owner')
    return render_template('dashboard.html', show_wallet=show_wallet)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
