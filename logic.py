from database import Vendor

def perform_login(username, password):
    # البحث عن المورد الذي يطابق اسم المستخدم وكلمة المرور معاً
    vendor = Vendor.query.filter_by(username=username, password=password).first()
    
    if vendor:
        return vendor, "تم تسجيل الدخول بنجاح إلى النظام اللامركزي."
    
    # فحص سبب الفشل لإظهار الرسالة العربية المتناسقة
    existing_user = Vendor.query.filter_by(username=username).first()
    if not existing_user:
        return None, "عذراً، هذا المستخدم غير مسجل في المنصة اللامركزية متطورة."
    else:
        return None, "كلمة المرور غير صحيحة، يرجى إعادة المحاولة."

def get_current_vendor(vendor_id):
    if vendor_id:
        return Vendor.query.get(vendor_id)
    return None
