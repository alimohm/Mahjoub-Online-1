from flask import session, flash
from models import AdminUser

def verify_admin_credentials(username, password):
    """
    منطق المطابقة المركزي لبرج المراقبة:
    يتحقق من البيانات ويرسل تنبيهات دقيقة للمستخدم.
    """
    try:
        # 1. البحث عن مدير النظام (Admin) في قاعدة البيانات
        admin = AdminUser.query.filter_by(username=username).first()
        
        # 2. التحقق من وجود الحساب أولاً
        if not admin:
            flash("🚫 هذا المستخدم غير مسجل في المنصة اللامركزية لـ محجوب أونلاين.", "warning")
            return False
        
        # 3. التحقق من مطابقة مفتاح الدخول (كلمة المرور)
        if admin.password != password:
            flash("⚠️ كلمة المرور غير صحيحة، يرجى التأكد والمحاولة مرة أخرى كمدير.", "danger")
            return False

        # 4. في حال النجاح: تفعيل الجلسة الأمنية لبرج المراقبة
        session['is_admin'] = True
        session['admin_user'] = admin.username
        
        flash(f"🛡️ تم تفعيل وصول برج المراقبة. مرحباً بك يا سيد {admin.username}", "success")
        return True

    except Exception as e:
        # تأمين النظام في حال حدوث خطأ تقني في قاعدة البيانات
        print(f"❌ خطأ في منطق الإدارة: {e}")
        flash("حدث خطأ تقني أثناء محاولة الاتصال ببرج المراقبة.", "danger")
        return False

def is_admin_logged_in():
    """
    صمام الأمان: يتحقق هل المتصفح يمتلك صلاحية الأدمن حالياً؟
    تستخدم لحماية المسارات الحساسة في app.py
    """
    return session.get('is_admin', False)

def logout_admin_logic():
    """
    تطهير الجلسة وتأمين النظام عند الخروج
    """
    session.pop('is_admin', None)
    session.pop('admin_user', None)
    flash("🔒 تم تسجيل الخروج من برج المراقبة بنجاح.", "info")
    return True
