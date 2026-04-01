import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db, init_db, Vendor

app = Flask(__name__)
# تأكد من أن Flask يرى مجلد القوالب بوضوح
app.template_folder = os.path.abspath('templates')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # منع التخزين المؤقت لضمان ظهور التعديلات فوراً
    return render_template('login.html')

@app.route('/')
def home():
    return redirect(url_for('login'))

if __name__ == "__main__":
    # تشغيل السيرفر على المنفذ 8080
    app.run(host='0.0.0.0', port=8080, debug=True)

from flask import Flask, render_template, request, redirect, url_for, session, flash
import logic # استدعاء العقل

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # إرسال البيانات للمنطق لمعالجتها
        result = logic.verify_login(request.form.get('username'), request.form.get('password'))
        
        if result['status']:
            session['vendor_id'] = result['user_id']
            session['role'] = result['role']
            return redirect(url_for('dashboard'))
        
        flash(result['message'], "error")
        
    return render_template('login.html')
