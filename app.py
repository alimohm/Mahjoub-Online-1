import os
from flask import Flask, render_template, request, redirect, url_for
from database import init_db
# استيراد الدوال الآن سيتم بنجاح تام
from logic import login_vendor, logout_vendor, is_logged_in, get_vendor_data

app = Flask(__name__)
init_db(app)

@app.route('/')
def login_page():
    if is_logged_in(): return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST']) # أضفنا GET هنا
def do_login():
    if request.method == 'GET':
        return redirect(url_for('login_page')) # إذا دخلت بالرابط، يرجعك لصفحة الدخول
    
    # هذا الجزء يبقى كما هو لمعالجة البيانات
    user = request.form.get('username')
    pw = request.form.get('password')
    if login_vendor(user, pw):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))
@app.route('/dashboard')
def dashboard():
    if not is_logged_in(): return redirect(url_for('login_page'))
    return f"مرحباً بك في لوحة تحكم {get_vendor_data().brand_name}"

@app.route('/logout')
def logout():
    return logout_vendor()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
