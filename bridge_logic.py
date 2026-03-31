import requests
import io
import json
from PIL import Image

# الإعدادات الأساسية - تم تحديث الرابط ليتجاوز بوابة الإدارة المتعثرة
GRAPHQL_URL = "https://api.qumra.cloud/graphql" 
ACCESS_TOKEN = "qmr_6efc3577-9287-4588-8c87-667e449d5397"

def calculate_final_price(original_price, currency):
    """تحويل العملة وإضافة نسبة الربح 30% (الحوكمة الرقمية)"""
    try:
        price = float(original_price)
        # تحويل من دولار إلى ريال سعودي إذا لزم الأمر
        if currency.upper() == 'USD':
            price = price * 3.8
        
        # إضافة هامش الربح والتقريب
        final_price = price * 1.30
        return round(final_price, 2)
    except (ValueError, TypeError):
        return 0.0

def process_product_image(uploaded_file):
    """تحويل الصورة إلى WebP لرفع أداء المتجر و SEO"""
    try:
        img = Image.open(uploaded_file)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        buffer = io.BytesIO()
        img.save(buffer, format="WebP", quality=80)
        buffer.seek(0)
        return buffer
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def push_to_qmr_store(name, description, final_price, image_buffer):
    """إرسال المنتج كمسودة إلى متجر محجوب أونلاين عبر GraphQL"""
    
    # الترويسات المطلوبة للاتصال بالسيرفر
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json",
    }

    # استعلام متوافق مع نظام Apollo لرفع الملفات
    query = """
    mutation CreateProduct($input: ProductInput!, $image: Upload) {
      createProduct(input: $input, image: $image) {
        id
        name
        status
      }
    }
    """
    
    # تجهيز العمليات (Operations)
    operations = {
        'query': query,
        'variables': {
            'input': {
                'name': name,
                'description': description,
                'price': float(final_price),
                'status': 'DRAFT',
                'currency': 'SAR'
            },
            'image': None  # سيتم ربطه عبر خريطة الملفات أدناه
        }
    }
    
    # خريطة الملفات (Map) لربط البافر بالمتغير variables.image
    map_data = {'0': ['variables.image']}
    
    try:
        # بناء الطلب متعدد الأجزاء (Multipart Request)
        files = {
            'operations': (None, json.dumps(operations), 'application/json'),
            'map': (None, json.dumps(map_data), 'application/json'),
            '0': ('product.webp', image_buffer, 'image/webp')
        }
        
        response = requests.post(GRAPHQL_URL, headers=headers, files=files)
        
        # طباعة النتيجة في سجلات ريلوي للمتابعة التقنية
        print(f"Qumra Status: {response.status_code}")
        print(f"Qumra Body: {response.text}")
        
        if response.status_code == 200 and "errors" not in response.text:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Connection Error to Qumra: {e}")
        return False
