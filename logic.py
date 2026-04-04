from flask import session
from werkzeug.security import check_password_hash
from models import Vendor

def login_vendor(u, p):
    """التحقق من دخول محجوب أونلاين بالاسم العربي"""
    if not u or not p:
        return False, "يرجى إدخال اسم المستخدم وكلمة المرور."

    clean_username = u.strip()
    vendor = Vendor.query.filter_by(username=clean_username).first()
    
    if vendor:
        if check_password_hash(vendor.password, p):
            session.clear()
            session['user_id'] = vendor.id
            session['role'] = 'vendor'
            session['username'] = vendor.username
            return True, f"تم الدخول بنجاح يا {vendor.brand_name}."
        else:
            return False, "كلمة المرور غير صحيحة."
    
    return False, "هذا الحساب غير مسجل في المنصة اللامركزية."

def is_logged_in():
    return session.get('role') == 'vendor' and 'user_id' in session
