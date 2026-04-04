from flask import session
from werkzeug.security import check_password_hash
from models import AdminUser

def verify_admin_credentials(u, p):
    """التحقق من دخول علي محجوب بالاسم العربي"""
    if not u or not p:
        return False, "يرجى إدخال بيانات الدخول."

    # .strip() هي السر هنا، فهي تحذف أي مسافات زائدة من الاسم العربي
    clean_username = u.strip()
    
    admin = AdminUser.query.filter_by(username=clean_username).first()
    
    if admin:
        # التحقق من كلمة المرور 123
        if check_password_hash(admin.password, p):
            session.clear()
            session['admin_id'] = admin.id
            session['role'] = 'admin'
            session['admin_user'] = admin.username
            return True, "تم الاتصال بنجاح. مرحباً بك يا مدير."
        else:
            return False, "خطأ في كلمة المرور، يرجى المحاولة مرة أخرى."
    
    return False, "هذا الاسم غير مسجل في سجلات الإدارة."

def is_admin_logged_in():
    return session.get('role') == 'admin' and 'admin_id' in session
