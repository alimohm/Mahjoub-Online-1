from flask import session
from werkzeug.security import check_password_hash
from models import Vendor
from database import db

def login_vendor(username, password):
    """
    التحقق من دخول المورد إلى المنصة اللامركزية.
    تنبيه: يتم التعامل مع التشفير والحالات السيادية (نشط/موقف).
    """
    try:
        # 1. البحث عن المستخدم في القاعدة
        vendor = Vendor.query.filter_by(username=username).first()

        # 2. إذا كان المستخدم غير موجود نهائياً
        if not vendor:
            return False, "تنبيه: اسم المستخدم هذا غير مسجل في المنصة اللامركزية."

        # 3. التحقق من كلمة المرور (مقارنة الشفرة الرقمية)
        if not check_password_hash(vendor.password, password):
            return False, "فشل تأمين البوابة: كلمة المرور غير صحيحة."

        # 4. فحص الحالة السيادية للمورد (Status)
        if vendor.status == 'blocked' or not vendor.is_active:
            return False, "وصول مرفوض: تم إيقاف صلاحيات هذا الحساب بقرار سيادي."
        
        if vendor.status == 'pending':
            return False, "بانتظار الاعتماد: حسابك لا يزال تحت مراجعة برج المراقبة."

        # 5. تفعيل الجلسة في حال النجاح
        session.clear() # تنظيف أي جلسات سابقة
        session['user_id'] = vendor.id
        session['username'] = vendor.username
        session['brand'] = vendor.brand_name
        session['role'] = 'vendor'
        
        # رسالة ترحيب خاصة بالمورد
        return True, f"أهلاً بك في سوقك الذكي، سيد {vendor.employee_name}."

    except Exception as e:
        return False, f"عطل فني في بوابة الدخول: {str(e)}"

def is_logged_in():
    """التحقق من وجود جلسة مورد نشطة"""
    return session.get('role') == 'vendor' and 'user_id' in session
