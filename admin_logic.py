# داخل admin_logic.py
if admin.password == p: # مقارنة نصية مباشرة لأن seed_system يضعها نصاً
    session.clear()
    session['role'] = 'super_admin'
    session['username'] = admin.username
    return True, "مرحباً بك يا مدير."
