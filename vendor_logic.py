from flask import session
from models import Vendor, VendorStaff

def login_vendor(u, p):
    # البحث عن مالك
    vendor = Vendor.query.filter_by(username=u).first()
    if vendor and vendor.password == p:
        session.clear()
        session['user_id'] = vendor.id
        session['role'] = 'vendor_owner' # يرى المحفظة
        session['username'] = vendor.username
        return True, "مرحباً بك يا سيد السوق الذكي"

    # البحث عن موظف
    staff = VendorStaff.query.filter_by(username=u).first()
    if staff and staff.password == p:
        session.clear()
        session['user_id'] = staff.vendor_id
        session['role'] = 'vendor_staff' # لا يرى المحفظة
        session['username'] = staff.username
        return True, "تم دخول الموظف بنجاح"
        
    return False, "بيانات الدخول غير صحيحة"
