from flask import session, flash, redirect, url_for
from database import Vendor

def login_vendor(username, password):
    """محرك التحقق من الهوية الرقمية للمورد"""
    vendor = Vendor.query.filter_by(username=username).first()
    
    if vendor and vendor.password == password:
        # تخزين بيانات الجلسة السيادية
        session['username'] = vendor.username
        session['brand_name'] = vendor.brand_name
        session['wallet'] = vendor.wallet_address
        flash(f"مرحباً بك مجدداً في نظام {vendor.brand_name}", "success")
        return True
    
    flash("خطأ في اسم المستخدم أو كلمة المرور.", "danger")
    return False

def is_logged_in():
    """التحقق من حالة البوابة (نشطة أم لا)"""
    return 'username' in session

def logout():
    """تطهير بيانات الجلسة وإغلاق البوابة"""
    session.clear()
    flash("تم تسجيل الخروج من النظام السيادي بنجاح.", "info")
    return redirect(url_for('login_page'))
