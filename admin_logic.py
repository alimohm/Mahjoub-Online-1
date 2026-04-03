from flask import session
from models import AdminUser

def is_admin_logged_in():
    """
    التحقق من حالة الجلسة (Session).
    تعيد True إذا كان 'صبري' قد سجل دخوله بنجاح.
    """
    return session.get('is_admin', False)

def verify_admin_credentials(username, password):
    """
    منطق المطابقة: 
    1. البحث عن اسم المستخدم في جدول AdminUser.
    2. التأكد من تطابق كلمة المرور (123).
    """
    try:
        # البحث عن المدير في قاعدة البيانات
        admin = AdminUser.query.filter_by(username=username).first()
        
        if admin and admin.password == password:
            # تخزين بيانات إضافية في الجلسة للترحيب به في الداشبورد
            session['admin_name'] = admin.username 
            return True
        
        return False
    except Exception as e:
        # في حال حدوث خطأ في الاتصال بقاعدة البيانات
        print(f"❌ خطأ إداري في التحقق: {e}")
        return False

def logout_admin():
    """
    تطهير الجلسة وتسجيل الخروج الآمن من برج المراقبة.
    """
    session.pop('is_admin', None)
    session.pop('admin_name', None)
    return True
