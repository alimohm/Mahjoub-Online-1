from flask import session, flash, redirect, url_for
from database import db, Vendor

# تأكد من وجود هذه الدالة تحديداً
def logout_vendor():
    session.clear()
    flash("تم تسجيل الخروج بنجاح من نظامك السيادي.", "info")
    return redirect(url_for('login_page'))

# بقية الدوال (login_vendor, is_logged_in, إلخ...)
def login_vendor(username, password):
    try:
        vendor = Vendor.query.filter_by(username=username).first()
        if vendor and vendor.password == password:
            session['vendor_id'] = vendor.id
            session['username'] = vendor.username
            session['brand_name'] = vendor.brand_name or "محجوب أونلاين"
            session['wallet'] = vendor.wallet_address
            return True
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def is_logged_in():
    return 'vendor_id' in session

def get_vendor_data():
    if is_logged_in():
        return Vendor.query.get(session['vendor_id'])
    return None
