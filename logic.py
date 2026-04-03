from flask import session, flash, redirect, url_for
from models import AdminUser

def verify_admin_credentials(username, password):
    """
    التحقق من بيانات الإدارة المركزية (برج المراقبة)
    بنفس أسلوب منطق الموردين.
    """
    # 1. محاولة جلب المدير من قاعدة البيانات (صبري)
    admin = AdminUser.query.filter_by(username=username).first()
    
    # 2. التحقق من وجود المستخدم في نظام الإدارة أولاً
    if not admin:
        flash("🚫 هذا المستخدم غير مسجل في المنصة اللامركزية لـ محجوب أونلاين.", "warning")
        return False
    
    # 3. التحقق من مطابقة كلمة المرور المركزية
    if admin.password != password:
        flash("⚠️ كلمة المرور غير صحيحة، يرجى التأكد والمحاولة مرة أخرى كمدير.", "danger")
        return False

    # 4. في حال التطابق التام، يتم تفعيل جلسة "برج المراقبة"
    session['is_admin'] = True
    session['admin_user'] = admin.username
    
    flash(f"🛡️ تم تفعيل برج المراقبة بنجاح. مرحباً بك يا سيد {admin.username}", "success")
    return True

def is_admin_logged_in():
    """التحقق من حالة جلسة الإدارة"""
    return session.get('is_admin', False)

def logout_admin():
    """تسجيل خروج آمن للمدير وتطهير الجلسة"""
    session.pop('is_admin', None)
    session.pop('admin_user', None)
    flash("🔒 تم الخروج من برج المراقبة وتأمين النظام بنجاح.", "info")
    return redirect(url_for('admin_login_route'))
