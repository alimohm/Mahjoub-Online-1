from flask import session, flash, redirect, url_for
from database import db, Vendor

def login_vendor(username, password):
    """منطق التحقق وحوكمة الدخول"""
    try:
        # البحث عن المورد في قاعدة البيانات السيادية
        vendor = Vendor.query.filter_by(username=username).first()
        
        if not vendor:
            flash("تنبيه: هذه الهوية الرقمية غير مسجلة في نظام MQ.", "warning")
            return False
            
        if vendor.password != password:
            flash("خطأ: المفتاح الخاص (كلمة المرور) غير مطابق.", "danger")
            return False
            
        # إنشاء جلسة عمل آمنة للمورد
        session['vendor_id'] = vendor.id
        session['brand_name'] = vendor.brand_name or "محجوب أونلاين"
        session['wallet'] = vendor.wallet_address
        return True
        
    except Exception as e:
        print(f"Logic Execution Error: {e}")
        flash("عذراً، حدث خطأ في مزامنة البيانات مع السيرفر.", "danger")
        return False

def logout():
    """تطهير الجلسة وإغلاق البوابة"""
    session.clear()
    flash("تم تسجيل الخروج بنجاح. نراك قريباً.", "info")
    return redirect(url_for('login_page'))

def is_logged_in():
    """فحص حالة الحوكمة للمستخدم الحالي"""
    return 'vendor_id' in session
