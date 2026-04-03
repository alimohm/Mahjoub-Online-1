from flask import session
from werkzeug.security import check_password_hash
from models import AdminUser

def verify_admin_credentials(username, password):
    """
    التحقق من بيانات الإدارة (برج المراقبة)
    قاعدتنا: أي شيء admin فهو للإدارة حصراً
    """
    # البحث في جدول الإدارة فقط
    admin = AdminUser.query.filter_by(username=username).first()
    
    if admin and check_password_hash(admin.password, password):
        # تنظيف الجلسة تماماً قبل تسجيل دخول الإدارة لمنع التداخل مع حساب المورد
        session.clear()
        
        # تخزين بيانات السيادة في الجلسة
        session['admin_id'] = admin.id
        session['admin_user'] = admin.username
        session['role'] = 'admin'
        return True, "تم فتح بوابات برج المراقبة بنجاح."
    
    return False, "عذراً، هذه البوابة للإدارة العليا فقط."

def is_admin_logged_in():
    """
    التحقق من صلاحيات الإدارة (تم إصلاح الخطأ في السطر 27)
    """
    return session.get('role') == 'admin' and 'admin_id' in session

def logout_admin_logic():
    """تأمين الخروج من برج المراقبة"""
    session.clear()
