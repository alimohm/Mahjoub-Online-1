import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db, init_db, Vendor
import logic

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'mahjoub_secret_2026')

# ربط قاعدة البيانات في ريلوي
init_db(app)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        
        # الربط المنطقي: التحقق من وجود المورد في Postgres
        vendor = Vendor.query.filter_by(username=u, password=p).first()
        
        if vendor:
            # إنشاء تذكرة الدخول (الجلسة)
            session['vendor_id'] = vendor.id
            return redirect(url_for('dashboard'))
        else:
            flash("خطأ في بيانات الدخول، يرجى التحقق من قاعدة البيانات")
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # منع الدخول إذا لم تكن هناك جلسة نشطة
    vendor_id = session.get('vendor_id')
    if not vendor_id:
        return redirect(url_for('login'))
    
    # سحب بيانات المورد الحقيقية لعرضها في الهيكل
    vendor = Vendor.query.get(vendor_id)
    return render_template('dashboard.html', vendor=vendor)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
