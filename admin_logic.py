from flask import session
from models import AdminUser

def verify_admin_credentials(u, p):
    """التحقق من دخول علي محجوب بالاسم العربي"""
    if not u or not p:
        return False, "يرجى إدخال بيانات الدخول."

    # تنظيف الاسم من المسافات الزائدة (مهم جداً للاسم العربي)
    clean_username = u.strip()
    
    # البحث عن 'علي محجوب' في قاعدة البيانات
    admin = AdminUser.query.filter_by(username=clean_username).first()
    
    if admin:
        # ملاحظة: نستخدم المقارنة المباشرة لأننا حقنا كلمة المرور كنص عادي في seed_system
        if admin.password == p:
            session.clear()
            session['admin_id'] = admin.id
            session['role'] = 'super_admin' # توحيد المسمى مع app.py
            session['username'] = admin.username
            return True, "تم الاتصال بنجاح. مرحباً بك يا مدير."
        else:
            return False, "خطأ في كلمة المرور، يرجى المحاولة مرة أخرى."
    
    return False, "هذا الاسم غير مسجل في سجلات الإدارة."

def is_admin_logged_in():
    return session.get('role') == 'super_admin' and 'admin_id' in session
