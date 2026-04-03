# admin_logic.py
from models import AdminUser
from werkzeug.security import check_password_hash
from flask import session

def verify_admin_credentials(username, password):
    # البحث في جدول المدراء (برج المراقبة)
    admin = AdminUser.query.filter_by(username=username).first()

    if not admin:
        return False, "فشل تأمين بوابة الإدارة: المستخدم غير معرّف."

    if not check_password_hash(admin.password, password):
        return False, "فشل تأمين بوابة الإدارة: كلمة المرور غير صحيحة."

    # الأدمن عادة لا يكون له حالات "قيد المراجعة" لأنه هو من يراجع، 
    # لكن يمكن إضافة نظام حماية إضافي هنا إذا لزم الأمر.

    session['admin_id'] = admin.id
    session['username'] = admin.username
    session['role'] = 'admin'
    return True, "تم الدخول إلى برج المراقبة السيادي."

def is_admin_logged_in():
    return session.get('role') == 'admin'
