import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db, init_db
import logic

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'mahjoub_king_2026')

# تهيئة قاعدة البيانات عند بدء التشغيل
init_db(app)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'vendor_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        
        # استدعاء المنطق المحدث لضمان المطابقة
        vendor_obj, message = logic.perform_login(u, p)
        
        if vendor_obj:
            session['vendor_id'] = vendor_obj.id
            return redirect(url_for('dashboard'))
        else:
            flash(message)
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    vendor_id = session.get('vendor_id')
    vendor = logic.get_current_vendor(vendor_id)
    
    if not vendor:
        return redirect(url_for('login'))
        
    return render_template('dashboard.html', vendor=vendor)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
