from database import init_db

# ... داخل الكود بعد تعريف app ...
init_db(app) # هذا السطر هو الذي "يفتح البوابة" بين الكود والقاعدة
import os
from flask import Flask, render_template, request, redirect, url_for
from config import Config
from database import db, init_db
# استيراد الدوال بالأسماء المتفق عليها
from logic import login_vendor, logout, is_logged_in

app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

@app.route('/')
def index():
    """تحويل تلقائي للبوابة السيادية"""
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    # منع الدخول المزدوج إذا كان المستخدم مسجلاً بالفعل
    if is_logged_in():
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # سحب البيانات من حقول الواجهة الأرجوانية
        user = request.form.get('username')
        pw = request.form.get('password')
        
        # تشغيل المنطق الذكي للتحقق
        if login_vendor(user, pw):
            return redirect(url_for('dashboard'))
        
        # في حال الفشل، الصفحة تنعش نفسها وتظهر رسالة الخطأ (Flash)
        return redirect(url_for('login_page'))

    # عرض الواجهة الملكية عند طلب الرابط (GET)
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """لوحة التحكم - المنطقة الآمنة"""
    if not is_logged_in():
        return redirect(url_for('login_page'))
    return render_template('dashboard.html')

@app.route('/logout')
def logout_route():
    return logout()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
