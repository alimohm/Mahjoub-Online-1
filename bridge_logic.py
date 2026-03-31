
# bridge_logic.py

def calculate_final_price(original_price, currency):
    """
    تقوم هذه الدالة بتحويل العملة وإضافة نسبة الربح 30%
    original_price: السعر الذي أدخله المورد
    currency: نوع العملة (USD أو SAR)
    """
    try:
        price = float(original_price)
        
        # 1. التحويل إلى ريال سعودي إذا كان السعر بالدولار
        if currency.upper() == 'USD':
            price = price * 3.8  # سعر الصرف المتفق عليه
        
        # 2. إضافة نسبة الربح 30% (الحوكمة الرقمية للربح)
        final_price = price * 1.30
        
        # 3. تقريب السعر لأقرب خانتين عشريتين ليكون احترافياً
        return round(final_price, 2)
        
    except ValueError:
        return 0.0

# ثابت إعدادات الوصول لمتجر قمرة (سنستخدمها في الخطوة القادمة)
GRAPHQL_URL = "https://mahjoub.online/admin/graphql"
ACCESS_TOKEN = "qmr_6efc3577-9287-4588-8c87-667e449d5397"
