from database import Vendor

def perform_login(username, password):
    """
    منطق تسجيل الدخول: التحقق المطابق مع قاعدة بيانات الموردين
    """
    # 1. البحث عن المورد باستخدام اسم المستخدم فقط
    vendor = Vendor.query.filter_by(username=username).first()
    
    # 2. التحقق من وجود المستخدم في قاعدة البيانات
    if not vendor:
        # رسالة تعزز مفهوم الحوكمة اللامركزية
        return None, "عذراً، هذا المستخدم غير مسجل في النظام اللامركزي للمنصة."
    
    # 3. المطابقة الدقيقة لكلمة المرور
    if vendor.password != password:
        return None, "كلمة المرور غير صحيحة، يرجى التحقق والمحاولة مرة أخرى."
    
    # 4. في حال المطابقة التامة، يتم إرجاع كائن المورد (Vendor Object)
    return vendor, "تم التحقق من الهوية الرقمية بنجاح."

def get_current_vendor(vendor_id):
    """
    جلب بيانات المورد الحالي من قاعدة البيانات لعرضها في الواجهة الملكية
    """
    if vendor_id:
        return Vendor.query.get(vendor_id)
    return None
