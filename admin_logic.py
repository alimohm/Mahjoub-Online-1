from flask import session
from models import AdminUser

def verify_admin_credentials(u, p):
    if not u or not p:
        return False, "يرجى إدخال اسم المستخدم وكلمة المرور."

    clean_username = u.strip()
    admin = AdminUser.query.filter_by(username=clean_username).first()
    
    if admin:
        if admin.password == p:
            session.clear()
            session['admin_id'] = admin.id
            session['role'] = 'super_admin'
            session['username'] = admin.username
            return True, "مرحباً بك يا مدير."
        else:
            return False, "كلمة المرور غير صحيحة."
            
    return False, "هذا الاسم غير مسجل."
