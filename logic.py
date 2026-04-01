from flask import session, flash, redirect, url_for
from database import db, Vendor

def login_vendor(username, password):
    """منطق التحقق وحوكمة الدخول للمنصة اللامركزية"""
    try:
        # 1. البحث عن المورد في قاعدة البيانات السيادية (Railway Postgres)
        vendor = Vendor.query.filter_by(username=username).first()
        
        # 2. التحقق من وجود الهوية الرقمية
        if not vendor:
            flash("تنبيه: هذه الهوية الرقمية غير مسجلة في المنصة اللامركزية.", "warning")
            return False
            
        # 3. التحقق من مطابقة المفتاح الخاص (كلمة المرور)
        if vendor.password != password:
            flash("خطأ: المفتاح الخاص (كلمة المرور) غير مطابق لسجلاتنا.", "danger")
            return False
            
        # 4. في حال النجاح: إنشاء جلسة عمل آمنة للمورد وتخزين بياناته
        session['vendor_id'] = vendor.id
        session['brand_name'] = vendor.brand_name or "محجوب أونلاين"
        session['wallet'] = vendor.wallet_address
        return True
        
    except Exception as e:
        print(f"Logic Execution Error: {e}")
        flash("عذراً، النظام يواجه صعوبة في مزامنة البيانات مع السيرفر السيادي الآن.", "danger")
        return False

def logout():
    """تطهير الجلسة وإغلاق بوابة الحوكمة"""
    session.clear()
    flash("تم تسجيل الخروج بنجاح من نظامك الإداري.", "info")
    return redirect(url_for('login_page'))

def is_logged_in():
    """فحص حالة الحوكمة للمستخدم الحالي (هل الجلسة نشطة؟)"""
    return 'vendor_id' in session
