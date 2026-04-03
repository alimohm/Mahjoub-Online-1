@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin_logged_in():
        return redirect(url_for('admin_login_route'))
    
    # جلب كل الموردين من الجدول الذي حدثناه
    all_vendors = Vendor.query.all()
    # جلب كل المنتجات التي تنتظر الموافقة (Pending)
    pending_products = Product.query.filter_by(status='pending').all()
    
    return render_template('admin_dashboard.html', 
                           vendors=all_vendors, 
                           pending_count=len(pending_products))
