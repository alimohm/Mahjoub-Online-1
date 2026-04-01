import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db, init_db
import logic # استيراد العقل المنفصل

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "mahjoub_2026_secret")
init_db(app)

@app.route('/')
def index():
    return redirect(url_for('login_view')) # توجيه للفيو الجديد

# تغيير اسم الدالة البرمجية إلى login_view مع بقاء الرابط /login
@app.route('/login', methods=['GET', 'POST'])
def login_view(): 
    if 'vendor_id' in session:
        return "تم تسجيل الدخول بنجاح" # أو وجهه للـ Dashboard

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # نطلب من المنطق تنفيذ التحقق
        result = logic.execute_authentication(username, password)
        
        if result['status']:
            session['vendor_id'] = result['user'].id
            return redirect(url_for('login_view'))
        
        flash(result['message'], "error")
        
    return render_template('login.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
