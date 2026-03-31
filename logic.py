from database import db, Vendor

def perform_login(username, password):
    """
    التحقق من بيانات المورد للدخول إلى نظام الحوكمة الرقمية.
    """
    # البحث المباشر لتقليل استهلاك موارد السيرفر في Railway
    vendor = Vendor.query.filter_by(username=username, password=password).first()
    
    if vendor:
        print(f"🔓 تم التحقق من هوية المورد: {username}")
        return vendor, "تم تسجيل الدخول بنجاح إلى النظام اللامركزي."
    
    # تحليل سبب الفشل لتقديم تجربة مستخدم (UX) أفضل
    existing_user = Vendor.query.filter_by(username=username).first()
    if not existing_user:
        return None, "عذراً، اسم المستخدم هذا غير موجود في قاعدة بيانات الموردين."
    else:
        return None, "كلمة المرور غير صحيحة، يرجى مراجعة بياناتك."

def get_current_vendor(vendor_id):
    """
    استدعاء بيانات المورد الحالي من الجلسة (Session).
    """
    if vendor_id:
        try:
            # استخدام get لجلب البيانات بسرعة عبر المفتاح الأساسي
            return Vendor.query.get(int(vendor_id))
        except (TypeError, ValueError):
            return None
    return None

def update_vendor_status(vendor_id, last_login_date):
    """
    (اختياري) لتحديث تاريخ آخر دخول للمورد لرفع مستوى الشفافية في سلاسل الإمداد.
    """
    vendor = Vendor.query.get(vendor_id)
    if vendor:
        vendor.last_login = last_login_date
        db.session.commit()
