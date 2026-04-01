from flask import session, flash, redirect, url_for
from database import db, Vendor

def login_vendor(username, password):
    vendor = Vendor.query.filter_by(username=username).first()
    if not vendor:
        flash("تنبيه: هذه الهوية الرقمية غير مسجلة في نظامنا.", "warning")
        return False
    if vendor.password != password:
        flash("خطأ: كلمة المرور غير مطابقة للمفتاح الخاص.", "danger")
        return False
    
    session['vendor_id'] = vendor.id
    session['brand_name'] = vendor.brand_name or "محجوب أونلاين"
    return True

def logout():
    """إصلاح خطأ ImportError وتطهير الجلسة"""
    session.clear()
    flash("تم تسجيل الخروج بنجاح من نظامك السيادي.", "info")
    return redirect(url_for('login_page'))

def is_logged_in():
    return 'vendor_id' in session
