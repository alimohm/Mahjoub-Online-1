from flask import session, flash, redirect, url_for
from database import Vendor

def login_vendor(username, password):
    vendor = Vendor.query.filter_by(username=username).first()
    if vendor and vendor.password == password:
        session['username'] = vendor.username
        session['brand_name'] = vendor.brand_name
        session['wallet'] = vendor.wallet_address
        flash(f"مرحباً بك في نظام {vendor.brand_name}", "success")
        return True
    flash("خطأ في بيانات الدخول.", "danger")
    return False

def is_logged_in():
    return 'username' in session

def logout():
    session.clear()
    flash("تم تسجيل الخروج بنجاح.", "info")
    return redirect(url_for('login_page'))
