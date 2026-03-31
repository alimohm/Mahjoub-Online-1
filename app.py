import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db, Vendor

app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

# --- منطق القاعدة وبداية التشغيل ---
with app.app_context():
    db.create_all() # إنشاء الجداول إذا لم تكن موجودة
    # إضافة حسابك "ali" تلقائياً لتتمكن من الدخول فوراً
    if not Vendor.query.filter_by(username="ali").first():
        admin = Vendor(
            username="ali", 
            password="123", 
            owner_name="علي محجوب", 
            brand_name="محجوب أونلاين"
        )
        db.session.add(admin)
        db.session.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Vendor.query.filter_by(username=request.form.get('username')).first()
        
        if user and user.password == request.form.get('password'):
            session['vendor_id'] = user.id
            return redirect(url_for('dashboard')) # تحويل للوحة التحكم عند النجاح
        
        flash("خطأ في اسم المستخدم أو كلمة المرور", "error")
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    vendor = Vendor.query.get(session['vendor_id'])
    return f"مرحباً بك يا {vendor.owner_name} في لوحة التحكم!"

if __name__ == "__main__":
    app.run(host
