from flask import session
from werkzeug.security import check_password_hash
from models import AdminUser

def verify_admin_credentials(username, password):
    admin = AdminUser.query.filter_by(username=username).first()
    if admin and check_password_hash(admin.password, password):
        session.clear()
        session['admin_id'] = admin.id
        session['admin_user'] = admin.username
        session['role'] = 'admin'
        return True, "تم الدخول لبرج المراقبة."
    return False, "بيانات الإدارة غير صحيحة."

def is_admin_logged_in():
    # إصلاح السطر 27 النهائي
    return session.get('role') == 'admin' and 'admin_id' in session
