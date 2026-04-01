# logic.py
from database import Vendor

def do_login_check(username, password): # غيرنا الاسم هنا لتجنب التعارض
    user = Vendor.query.filter_by(username=username).first()
    if user and user.password == password:
        return {"status": True, "user": user}
    return {"status": False, "message": "بيانات غير صحيحة"}
