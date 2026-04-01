from database import Vendor

def do_auth(u, p):
    # البحث المباشر في المنصة اللامركزية
    user = Vendor.query.filter_by(username=u).first()
    if not user:
        return {"status": False, "msg": "اسم المستخدم غير مسجل في المنصة اللامركزية"}
    if user.password != p:
        return {"status": False, "msg": "كلمة المرور غير صحيحة"}
    return {"status": True, "user": user}
