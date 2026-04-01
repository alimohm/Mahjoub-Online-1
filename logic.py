from flask import session, flash, redirect, url_for
from database import db, Vendor

def login_vendor(username, password):
    """التحقق من بيانات المورد وتخزين هويته في الجلسة"""
    try:
        # البحث عن المورد في قاعدة البيانات
        vendor = Vendor.query.filter_by(username=username).first()
        
        if vendor and vendor.password == password:
            # تخزين البيانات الأساسية في الـ Session
            session['vendor_id'] = vendor.id
            session['username'] = vendor.username
            session['brand_name'] = vendor.brand_name or f"متجر {vendor.username}"
            session['wallet'] = vendor.wallet_address # محفظة MAH
            
            flash(f"أهلاً بك في منصتك السيادية، {vendor.owner_name or vendor.username}", "success")
            return True
        else:
            flash("خطأ في اسم المستخدم أو كلمة المرور. يرجى التحقق.", "danger")
            return False
            
    except Exception as e:
        # التعامل مع أخطاء قاعدة البيانات (مثل العمود المفقود)
        print(f"Logic Error: {e}")
        flash("عذراً، حدث خطأ فني في النظام. جاري الإصلاح تلقائياً.", "warning")
        return False

def get_current_vendor():
    """جلب بيانات المورد الحالي المسجل دخوله"""
    if 'vendor_id' in session:
        return Vendor.query.get(session['vendor_id'])
    return None

def logout_vendor():
    """إنهاء الجلسة والخروج"""
    session.clear()
    flash("تم تسجيل الخروج من سوقك الذكي بنجاح.", "info")
    return redirect(url_for('login_page'))
