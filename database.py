from database import Vendor

def do_auth(u, p):
    """التحقق المباشر من قاعدة البيانات"""
    # البحث عن اسم المستخدم في جدول vendor
    user = Vendor.query.filter_by(username=u).first()
    
    if not user:
        return {"status": False, "msg": "اسم المستخدم غير مسجل في المنصة اللامركزية"}
    
    # التحقق من كلمة المرور
    if user.password != p:
        return {"status": False, "msg": "كلمة المرور غير صحيحة"}
    
    return {"status": True, "user": user}
