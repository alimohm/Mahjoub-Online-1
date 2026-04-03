from flask import session
from werkzeug.security import check_password_hash
# استيراد المورد وقاعدة البيانات (تأكد من صحة مسار الاستيراد حسب ملفاتك)
from models import Vendor 
from database import db 

def login_vendor(username, password):
    try:
        # 1. البحث عن المورد في قاعدة البيانات المرتبطة
        vendor = Vendor.query.filter_by(username=username).first()

        # 2. التحقق من الوجود
        if not vendor:
            return False, "المستخدم غير مسجل في المنصة اللامركزية."

        # 3. التحقق من كلمة المرور المشفرة
        if not check_password_hash(vendor.password, password):
            return False, "فشل تأمين البوابة: كلمة المرور غير صحيحة."

        # 4. مراجعة الحالات السيادية (المنطق الذي طلبته)
        status = vendor.status.lower() if vendor.status else 'pending'

        if status == 'blocked': # موقف
            return False, "وصول مرفوض: تم حظر حسابك بقرار سيادي."
        
        elif status == 'restricted': # مقيد
            return False, "حساب مقيد: صلاحياتك معلقة حالياً."
        
        elif status == 'pending': # تحت المراجعة
            return False, "الدخول معلق: حسابك لا يزال تحت المراجعة الفنية."

        # 5. إذا اجتاز الاختبارات (تفعيل الجلسة)
        session.clear() # تنظيف الجلسة القديمة للأمان
        session['user_id'] = vendor.id
        session['username'] = vendor.username
        session['role'] = 'vendor'
        
        # حالة "تحت الرقابة"
        if status == 'under_surveillance':
            session['surveillance_mode'] = True
            return True, "تنبيه: أنت الآن تحت نظام الرقابة الرقمية المستمرة."

        return True, "تم الدخول بنجاح إلى منصة الموردين."

    except Exception as e:
        # في حال حدوث خطأ في الاتصال بقاعدة البيانات
        return False, f"خطأ في الاتصال بالمنصة: {str(e)}"

def is_logged_in():
    """التحقق من حالة تسجيل الدخول للمورد"""
    return session.get('role') == 'vendor' and 'user_id' in session
