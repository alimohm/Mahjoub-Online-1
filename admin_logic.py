from flask import session
from models import AdminUser

def verify_admin_credentials(u, p):
    """
    تحقق منطقي ذكي:
    1. التأكد من وجود المستخدم.
    2. التأكد من صحة كلمة المرور.
    3. إرجاع رسائل مخصصة للوعي الأمني.
    """
    
    # تنظيف المدخلات
    clean_username = u.strip() if u else ""
    
    if not clean_username or not p:
        return False, "يرجى إدخال بيانات الدخول كاملة."

    # الخطوة 1: البحث عن المستخدم في المنصة
    admin = AdminUser.query.filter_by(username=clean_username).first()
    
    if not admin:
        # إذا لم يجد الاسم في قاعدة البيانات
        return False, "هذا الاسم غير مسجل في المنصة اللامركزية."

    # الخطوة 2: فحص كلمة المرور بعد التأكد من وجود الحساب
    if admin.password != p:
        # إذا وجد الحساب ولكن كلمة المرور لم تتطابق
        return False, "كلمة المرور غير صحيحة، يرجى المحاولة مرة أخرى."

    # الخطوة 3: نجاح عملية التحقق
    session.clear()
    session['admin_id'] = admin.id
    session['role'] = 'super_admin'
    session['username'] = admin.username
    
    return True, "تم التحقق بنجاح. مرحباً بك في مركز القيادة."
