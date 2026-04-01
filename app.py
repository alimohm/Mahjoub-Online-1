import os
from flask import Flask, render_template, request, redirect, url_for, session
from config import Config
from database import db, init_db
from logic import login_vendor, logout, is_logged_in

# إنشاء تطبيق Flask وتطبيق الإعدادات السيادية
app = Flask(__name__)
app.config.from_object(Config)

# ربط المحرك بقاعدة البيانات في Railway
init_db(app)

@app.route('/')
def index():
    """المسار الرئيسي: بوابة العبور الذكية"""
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """بوابة الدخول الموحدة (عرض الواجهة ومعالجة البيانات)"""
    # منع الدخول المتكرر إذا كانت الجلسة نشطة
    if is_logged_in():
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # سحب الهوية الرقمية من الواجهة
        user = request.form.get('username')
        pw = request.form.get('password')
        
        # تشغيل محرك التحقق المنطقي
        if login_vendor(user, pw):
            return redirect(url_for('dashboard'))
        
        # إعادة التوجيه في حال الفشل لتفعيل رسائل التنبيه
        return redirect(url_for('login_page'))

    # عرض التصميم الملكي الأرجواني (GET)
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """لوحة التحكم السيادية - المنطقة الآمنة للمورد"""
    if not is_logged_in():
        flash("يجب تسجيل الدخول للوصول إلى النظام السيادي.", "warning")
        return redirect(url_for('login_page'))
    
    # سيتم عرض واجهة Dashboard المتجاوبة هنا
    return render_template('dashboard.html')

@app.route('/logout')
def logout_route():
    """إغلاق البوابة وتطهير البيانات"""
    return logout()

if __name__ == '__main__':
    # ضبط المنفذ ليتوافق مع بيئة تشغيل Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
