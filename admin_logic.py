from flask import session
from werkzeug.security import check_password_hash
from models import Vendor

def login_vendor(u, p):
    """منطق دخول الموردين - التحقق الصارم من الهوية"""
    if not u or not p:
        return False, "يرجى إدخال اسم المستخدم وكلمة المرور."

    # 1. البحث عن المورد في القاعدة
    vendor = Vendor.query.filter_by(username=u).first()
    
    # حالة 1: الحساب غير موجود
    if not vendor:
        return False, "عذراً، هذا الحساب غير مسجل في المنصة اللامركزية."
    
    # حالة 2: التحقق من كلمة المرور
    if check_password_hash(vendor.password, p):
        session.clear()
        session['user_id'] = vendor.id
        session['role'] = 'vendor'
        session['username'] = vendor.username
        return True, f"تم الاتصال بنجاح. أهلاً بك يا {vendor.brand_name}."
    
    # حالة 3: كلمة المرور خطأ
    else:
        return False, "كلمة المرور غير صحيحة، يرجى التأكد من مفاتيح الدخول."

def is_logged_in():
    """هذه هي الدالة التي يطلبها السيرفر وينهار بسبب فقدانها"""
    return session.get('role') == 'vendor' and 'user_id' in session
