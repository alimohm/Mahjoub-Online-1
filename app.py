import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db, init_db
import logic
import bridge_logic

app = Flask(__name__)
# مفتاح تشفير الجلسات - استبدله بمتغير بيئة في Railway لاحقاً
app.secret_key = os.environ.get('SECRET_KEY', 'mahjoub_online_sovereign_2026')

# تهيئة الاتصال بقاعدة البيانات
init_db(app)

@app.route('/')
def index():
    if 'vendor_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'vendor_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        
        # منطق التحقق والمطابقة الحقيقي
        vendor, message = logic.perform_login(u, p)
        
        if vendor:
            session['vendor_id'] = vendor.id
            return redirect(url_for('dashboard'))
        else:
            flash(message)
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # منع الدخول غير المصرح به للهيكل
    v_id = session.get('vendor_id')
    if not v_id:
        return redirect(url_for('login'))
        
    # جلب بيانات المورد الحقيقية من القاعدة لعرضها في الهيكل
    vendor = logic.get_current_vendor(v_id)
    if not vendor:
        session.clear()
        return redirect(url_for('login'))
        
    return render_template('dashboard.html', vendor=vendor)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    # التوافق مع منافذ Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
