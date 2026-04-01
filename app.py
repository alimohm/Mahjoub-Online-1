import os
from flask import Flask, render_template, request, redirect, url_for, session
from database import init_db
from logic import login_vendor, logout_vendor, is_logged_in, get_vendor_data

app = Flask(__name__)

# 1. تهيئة قاعدة البيانات والإصلاح التلقائي للهيكل
init_db(app)

# --- المسارات (Routes) ---

@app.route('/')
def login_page():
    """عرض بوابة الدخول السيادية"""
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    """معالجة بيانات تسجيل الدخول"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    # استخدام المنطق الذكي للتحقق
    if login_vendor(username, password):
        return redirect(url_for('dashboard'))
    
    return redirect(url_for('login_page'))

@app.route('/dashboard')
def dashboard():
    """لوحة التحكم الملكية - تعرض بيانات المحفظة والبراند"""
    if not is_logged_in():
        return redirect(url_for('login_page'))
    
    vendor = get_vendor_data()
    return render_template('dashboard.html', vendor=vendor)

@app.route('/logout')
def logout():
    """تسجيل الخروج الآمن"""
    return logout_vendor()

# --- تشغيل السيرفر ---
if __name__ == '__main__':
    # Railway يستخدم المنفذ 8080 تلقائياً
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
