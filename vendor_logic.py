from flask import session
from models import Vendor, VendorStaff

def login_vendor(u, p):
    # 1. فحص الملاك (الموردين)
    vendor = Vendor.query.filter_by(username=u).first()
    if vendor and vendor.password == p:
        session.clear()
        session['user_id'] = vendor.id
        session['role'] = 'vendor_owner' # هذا هو المفتاح للدخول للدشبورد
        session['username'] = vendor.username
        session['brand'] = vendor.brand_name
        return True, "مرحباً بك في محجوب أونلاين."

    # 2. فحص الموظفين
    staff = VendorStaff.query.filter_by(username=u).first()
    if staff and staff.password == p:
        session.clear()
        session['user_id'] = staff.vendor_id
        session['role'] = 'vendor_staff'
        session['username'] = staff.username
        session['brand'] = staff.owner.brand_name
        return True, "تم دخول الموظف بنجاح."
        
    return False, "بيانات الدخول غير صحيحة."
