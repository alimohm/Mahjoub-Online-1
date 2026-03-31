
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
        

import requests

def push_to_qmr_store(name, description, final_price, image_buffer):
    """
    تقوم هذه الدالة بإرسال البيانات النهائية لمتجر محجوب أونلاين عبر GraphQL
    وتعيين حالة المنتج كـ 'مسودة' (DRAFT) للمراجعة.
    """
    
    # 1. تجهيز الترويسات (Headers) المطلوبة من قمرة
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }

    # 2. بناء استعلام GraphQL لإنشاء المنتج
    # ملاحظة: نرسله كمسودة (DRAFT) لضبط الحوكمة الرقمية
    query = """
    mutation CreateProduct($input: ProductInput!) {
      createProduct(input: $input) {
        id
        name
        status
      }
    }
    """
    
    variables = {
        "input": {
            "name": name,
            "description": description,
            "price": final_price,
            "status": "DRAFT",  # سيظهر عندك للمراجعة أولاً
            "currency": "SAR"   # المتجر بالريال السعودي
        }
    }

    # 3. إرسال الطلب (هنا نرسل البيانات والصورة معاً)
    try:
        # تجهيز ملف الصورة المعالج بصيغة WebP
        files = {
            'image': ('product.webp', image_buffer, 'image/webp')
        }
        
        response = requests.post(
            GRAPHQL_URL,
            json={'query': query, 'variables': variables},
            headers=headers,
            files=files
        )
        
        if response.status_code == 200:
            print("تم إرسال المنتج لمتجر محجوب أونلاين بنجاح (قيد المراجعة)")
            return True
        else:
            print(f"خطأ في الإرسال: {response.text}")
            return False
            
    except Exception as e:
        print(f"حدث خطأ أثناء الاتصال بقمرة: {e}")
        return False
