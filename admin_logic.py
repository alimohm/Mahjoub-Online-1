from flask import session
from werkzeug.security import check_password_hash
from models import AdminUser

def verify_admin_credentials(u, p):
    """منطق الإدارة الصارم - علي محجوب"""
    if not u or not p:
        return False, "يرجى إدخال بيانات الإدارة."

    # البحث عن المدير (AdminUser وليس Vendor)
    admin = AdminUser.query.filter_by(username=u).first()
    
    if not admin:
        return False, "تنبيه: هذا المعرف غير مسجل في الإدارة المركزية."
    
    if check_password_hash(admin.password, p):
        session.clear()
        session['admin_id'] = admin.id
        session['role'] = 'admin'
        session['admin_user'] = admin.username
        return True, "تم تأكيد الصلاحيات يا علي."
    
    return False, "خطأ في كلمة المرور لبرج المراقبة."

def is_admin_logged_in():
    return session.get('role') == 'admin' and 'admin_id' in session
