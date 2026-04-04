from models import Vendor, VendorStaff, Wallet

def login_vendor(u, p):
    # 1. البحث أولاً في جدول الموردين (الملاك)
    vendor = Vendor.query.filter_by(username=u).first()
    
    if vendor:
        # أ: التحقق من الحالة (محظور أم نشط)
        if not vendor.is_active or vendor.status == "محظور":
            return False, "❌ عذراً، حسابك محظور. يرجى التواصل مع الإدارة المركزية.", None
        
        # ب: التحقق من كلمة المرور
        if vendor.password == p:
            return True, f"مرحباً بك يا سيد {vendor.username} في مملكتك الرقمية", "vendor_owner"
        else:
            return False, "🔑 عذراً، كلمة المرور غير صحيحة. حاول مجدداً.", None

    # 2. إذا لم يكن مورداً، نبحث في جدول الموظفين
    staff = VendorStaff.query.filter_by(username=u).first()
    
    if staff:
        # التحقق من حالة المورد الأصلي (هل صاحب العمل محظور؟)
        if not staff.owner.is_active or staff.owner.status == "محظور":
            return False, "❌ لا يمكن الدخول، حساب المورد التابع له الموظف محظور حالياً.", None
            
        if staff.password == p:
            return True, f"مرحباً بك {staff.username} (دخول موظف مصرح)", "vendor_staff"
        else:
            return False, "🔑 كلمة المرور للموظف غير صحيحة.", None

    # 3. إذا لم يجد الاسم في الجدولين نهائياً
    return False, "🚫 هذا الحساب غير مسجل في المنصة اللامركزية. تأكد من البيانات.", None
