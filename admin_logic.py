from flask import session, request
from models import AdminUser, Vendor, Wallet, db

def verify_admin_credentials(u, p):
    """
    تحقق منطقي ذكي لدخول المسؤول مع تنظيف الجلسة
    """
    clean_username = u.strip() if u else ""
    
    if not clean_username or not p:
        return False, "يرجى إدخال بيانات الدخول كاملة."

    # استخدام filter بدلاً من filter_by لضمان دقة الاستعلام في بعض نسخ SQLAlchemy
    admin = AdminUser.query.filter(AdminUser.username == clean_username).first()
    
    if not admin:
        return False, "هذا الاسم غير مسجل في المنصة اللامركزية."

    if admin.password != p:
        return False, "كلمة المرور غير صحيحة، يرجى المحاولة مرة أخرى."

    # تأمين الجلسة
    session.clear()
    session['admin_id'] = admin.id
    session['role'] = 'super_admin'
    session['username'] = admin.username
    
    return True, "تم التحقق بنجاح. مرحباً بك في مركز القيادة."

def get_admin_stats():
    """
    دالة الإحصائيات المخصصة للوحة الرئيسية (Dashboard)
    محسنة لتعمل بسرعة عالية جداً
    """
    try:
        # استخدام count() مباشرة على مستوى الاستعلام لتوفير الذاكرة
        total_v = db.session.query(Vendor).count()
        total_w = db.session.query(Wallet).count()
        return {
            'total_vendors': total_v,
            'active_wallets': total_w
        }
    except Exception as e:
        print(f"⚠️ خطأ في جلب الإحصائيات: {e}")
        return {'total_vendors': 0, 'active_wallets': 0}

def manage_accounts_logic():
    """
    جلب كافة الموردين لعرضهم في لوحة الاعتماد حصراً
    مرتبين من الأحدث إلى الأقدم
    """
    return Vendor.query.order_by(Vendor.id.desc()).all()

def create_vendor_logic():
    """
    المنطق السيادي لإنشاء مورد وتفعيل محفظته تلقائياً (MAH-XXXX)
    يضمن عدم حدوث تضارب في قاعدة البيانات
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        brand_name = request.form.get('brand_name', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            return False, "اسم المستخدم وكلمة المرور متطلبات أساسية."

        # فحص التكرار
        if Vendor.query.filter_by(username=username).first():
            return False, "اسم المستخدم هذا محجوز مسبقاً لمورد آخر."

        try:
            # 1. إنشاء سجل المورد الجديد
            new_vendor = Vendor(
                username=username,
                brand_name=brand_name,
                password=password, 
                status="نشط",
                is_active=True
            )
            db.session.add(new_vendor)
            db.session.flush() # توليد ID المورد لاستخدامه في المحفظة قبل Commit

            # 2. توليد المحفظة السيادية وربطها بالمورد
            new_wallet = Wallet(vendor_id=new_vendor.id)
            db.session.add(new_wallet)
            
            db.session.commit()
            return True, f"✅ تم اعتماد {brand_name} وتفعيل محفظة MAH السيادية بنجاح."
            
        except Exception as e:
            db.session.rollback() # تراجع عن العمليات في حال حدوث أي خطأ
            return False, f"❌ تعذر إتمام العملية: {str(e)}"

    return False, "طلب غير صالح."
