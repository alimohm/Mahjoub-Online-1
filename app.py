import os
import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db, init_db, Vendor
import logic

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'mahjoub_sovereign_2026')
init_db(app)

# إعدادات المتجر
MAHJOUB_API_KEY = "qmr_dcbbd1f6-d0a7-43ed-9b4c-4a9394be06b9"
STORE_URL = "https://mahjoub.online/api/v1/products"
CONVERSION_RATE = 3.8  # سعر تحويل الدولار للريال السعودي
PROFIT_MARGIN = 1.30   # إضافة 30% تلقائياً

@app.route('/add_product', methods=['POST'])
def add_product():
    vendor_id = session.get('vendor_id')
    if not vendor_id: return redirect(url_for('login'))
    
    vendor = Vendor.query.get(vendor_id)
    
    # 1. استلام البيانات من النافذة
    name = request.form.get('name')
    raw_price = float(request.form.get('price')) # السعر الذي أدخله المورد
    currency = request.form.get('currency')      # العملة المختارة (USD أو SAR)
    description = request.form.get('description')

    # 2. منطق تحويل العملات وتوحيدها (الريال السعودي هو الأساس)
    if currency == "USD":
        base_price = raw_price * CONVERSION_RATE
    else:
        base_price = raw_price

    # 3. إضافة هامش ربح المنصة (30%) تلقائياً
    final_price_sar = round(base_price * PROFIT_MARGIN, 2)

    # 4. تجهيز الحمولة للأدوات (مع حالة المسودة)
    payload = {
        "api_key": MAHJOUB_API_KEY,
        "vendor_wallet": vendor.wallet_address,
        "product_name": name,
        "price_sar": final_price_sar,
        "description": description,
        "status": "draft",  # يظهر كمسودة للمراجعة
        "original_currency": currency,
        "vendor_cost": raw_price
    }

    try:
        # إرسال البيانات عبر الأدوات البرمجية
        response = requests.post(STORE_URL, json=payload, timeout=10)
        
        if response.status_code == 200 or response.status_code == 201:
            flash(f"تم رفع '{name}' كمسودة. السعر النهائي بعد إضافة 30%: {final_price_sar} ر.س")
        else:
            flash("تنبيه: تم استقبال المنتج ولكن حدث خطأ في أدوات الربط.")
    except Exception as e:
        flash("خطأ في الاتصال بالمتجر، يرجى المحاولة لاحقاً.")

    return redirect(url_for('dashboard'))

# بقية المسارات (login, dashboard, logout) تظل كما هي في الكود السابق
