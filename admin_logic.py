from models import AdminUser
from werkzeug.security import check_password_hash
from flask import session

def verify_admin_credentials(username, password):
    # البحث في جدول الإدارة فقط
    admin = AdminUser.query.filter_by(username=username).first()
    if admin and check_password_hash(admin.password, password):
        session['admin_id'] = admin.id
        session['role'] = 'admin'
        session['admin_user'] = admin.username
        return True, "تم الدخول لبرج المراقبة بنجاح"
    return False, "عذراً، هذه البوابة للإدارة فقط"

def is_admin_logged_in():
    return session.get('role') == 'admin'
