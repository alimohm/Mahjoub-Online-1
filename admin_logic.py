from flask import session
from werkzeug.security import check_password_hash
from models import AdminUser

def verify_admin_credentials(username, password):
    """منطق دخول برج المراقبة (الإدارة)"""
    admin = AdminUser.query.filter_by(username=username).first()
    
    # 1. التحقق من وجود الحساب
    if not admin:
        return False, "تنبيه: هذا المعرف غير مسجل ضمن طاقم الإدارة المركزية."
    
    # 2. التحقق من كلمة المرور
    if not check_password_hash(admin.password, password):
        return False, "خطأ في كلمة المرور: لا تملك صلاحية الوصول لبرج المراقبة."

    # نجاح الدخول
    session.clear()
    session['admin_id'] = admin.id
    session['role'] = 'admin'
    session['admin_user'] = admin.username
    return True, "تم تأكيد الصلاحيات. مرحباً بك في لوحة التحكم المركزية."

def is_admin_logged_in():
    return session.get('role') == 'admin' and 'admin_id' in session
