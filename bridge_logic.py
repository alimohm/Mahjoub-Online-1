
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

from PIL import Image
import io

def process_product_image(uploaded_file):
    """
    تستقبل هذه الدالة أي صورة مرفوعة، وتحولها إلى WebP 
    لضمان خفة الوزن وسرعة المتجر.
    """
    try:
        # فتح الصورة الأصلية
        img = Image.open(uploaded_file)
        
        # تحويلها إلى صيغة RGB (للتأكد من توافق الألوان)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        # حفظ الصورة في الذاكرة بصيغة WebP
        buffer = io.BytesIO()
        img.save(buffer, format="WebP", quality=80) # جودة 80% توازن بين الوضوح والحجم
        buffer.seek(0)
        
        return buffer
        
    except Exception as e:
        print(f"Error processing image: {e}")
        return None
        
