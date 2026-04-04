from flask import session
from werkzeug.security import check_password_hash
from models import Vendor

def login_vendor(u, p):
    """منطق الموردين - المنصة اللامركزية"""
    vendor = Vendor.query.filter_by(username=u).first()
    
    if not vendor:
        return False, "عذراً، هذا الحساب غير مسجل في المنصة اللامركزية."
    
    if check_password_hash(vendor.password, p):
        session.clear()
        session['user_id'] = vendor.id
        session['role'] = 'vendor'
        return True, f"تم الاتصال بنجاح يا {vendor.brand_name}."
    
    return False, "كلمة المرور غير صحيحة."

def is_logged_in():
    return session.get('role') == 'vendor' and 'user_id' in session
