# ... الكود السابق (مسارات الموردين وغيرها) ...

# ==========================================
# --- مسارات الإدارة المركزية (Admin) ---
# ==========================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login_route():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard_route'))
    
    if request.method == 'POST':
        u = request.form.get('admin_user')
        p = request.form.get('admin_pass')
        if verify_admin_credentials(u, p):
            return redirect(url_for('admin_dashboard_route'))
            
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard_route():
    if not is_admin_logged_in(): # صمام الأمان
        return redirect(url_for('admin_login_route'))
    
    # 1. جلب قائمة كل الموردين في المنصة
    all_vendors = Vendor.query.all()
    
    # 2. جلب المنتجات التي تنتظر موافقتك (Pending)
    pending_products = Product.query.filter_by(status='pending').all()
    
    # 3. إرسال هذه البيانات للهيكل ليعرضها فوراً
    return render_template('admin_dashboard.html', 
                           vendors=all_vendors, 
                           pending_count=len(pending_products))

@app.route('/admin/logout')
def admin_logout():
    logout_admin_logic() # تنظيف جلسة الإدارة
    return redirect(url_for('admin_login_route'))

# --- تسجيل الخروج العام ---
@app.route('/logout')
def logout_route():
    session.clear() 
    flash("تم تسجيل الخروج من النظام اللامركزي.", "info")
    return redirect(url_for('login_page'))

# --- تشغيل السيرفر (يجب أن يكون في النهاية دائماً) ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
