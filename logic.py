from database import Vendor

def do_auth(u, p):
    """التحقق وسحب الهوية السيادية"""
    user = Vendor.query.filter_by(username=u).first()
    
    if not user:
        return {"status": False, "msg": "المستخدم غير مسجل في المنصة اللامركزية"}
    
    if user.password != p:
        return {"status": False, "msg": "كلمة المرور غير صحيحة"}
    
    # إرجاع كائن المستخدم كاملاً ليتم تخزينه في الجلسة
    return {"status": True, "user": user}
