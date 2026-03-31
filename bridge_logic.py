# bridge_logic.py

import requests
import io
import json
from PIL import Image

# الإعدادات الأساسية
GRAPHQL_URL = "https://mahjoub.online/admin/graphql" # جرب هذا الرابط المباشر إذا فشل رابط الدومين
ACCESS_TOKEN = "qmr_6efc3577-9287-4588-8c87-667e449d5397"

def calculate_final_price(original_price, currency):
    try:
        price = float(original_price)
        if currency.upper() == 'USD':
            price = price * 3.8
        final_price = price * 1.30
        return round(final_price, 2)
    except ValueError:
        return 0.0

def process_product_image(uploaded_file):
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
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }

    # تعديل الاستعلام لدعم رفع الملفات بشكل صحيح
    query = """
    mutation CreateProduct($input: ProductInput!, $image: Upload!) {
      createProduct(input: $input, image: $image) {
        id
        name
      }
    }
    """
    
    # خريطة الربط (Mapping) لإخبار السيرفر أين يضع ملف الصورة
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
            'image': None
        }
    }
    
    map_data = {'0': ['variables.image']}
    
    try:
        files = {
            'operations': (None, json.dumps(operations), 'application/json'),
            'map': (None, json.dumps(map_data), 'application/json'),
            '0': ('product.webp', image_buffer, 'image/webp')
        }
        
        response = requests.post(GRAPHQL_URL, headers=headers, files=files)
        
        # لغرض التصحيح: اطبع النتيجة في سجلات Railway
        print(f"Response: {response.status_code} - {response.text}")
        
        if response.status_code == 200 and "errors" not in response.text:
            return True
        return False
            
    except Exception as e:
        print(f"Connection Error: {e}")
        return False
