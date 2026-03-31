import requests
import io
import json
from PIL import Image

# 1. الإعدادات السيادية لمنصة محجوب أونلاين
GRAPHQL_URL = "https://mahjoub.online/admin/graphql"

# المفتاح الجديد ذو الصلاحيات الكاملة (الذي قمنا بإنشائه وتسميته Mahjoub-Vendors-Key)
ACCESS_TOKEN = "qmr_dcbbd1f6-d0a7-43ed-9b4c-4a9394be06b9"

def calculate_final_price(original_price, currency):
    """تحويل العملة وإضافة نسبة الربح 30% (نظام الحوكمة الرقمية)"""
    try:
        price = float(original_price)
        # التحويل من دولار إلى ريال سعودي بمعدل ثابت 3.8 لضمان استقرار السعر
        if str(currency).upper() == 'USD':
            price = price * 3.8
        
        # إضافة هامش الربح (30%) لدعم نمو المنصة
        final_price = price * 1.30
        return round(final_price, 2)
    except (ValueError, TypeError):
        return 0.0

def process_product_image(uploaded_file):
    """تحويل الصورة إلى WebP لرفع أداء المتجر وتحسين الـ SEO لظهورك في جوجل"""
    try:
        img = Image.open(uploaded_file)
        
        # تحويل الألوان لضمان التوافق مع صيغة WebP
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        
        buffer = io.BytesIO()
        # ضغط الصورة بجودة 80 لرفع سرعة التحميل (رفع الدوبامين للمستهلك)
        img.save(buffer, format="WebP", quality=80)
        buffer.seek(0)
        return buffer
    except Exception as e:
        print(f"❌ خطأ في معالجة الصورة: {e}")
        return None

def push_to_mahjoub_store(name, description, final_price, image_buffer, vendor_id):
    """إرسال بيانات المنتج مباشرة إلى نقطة اتصال mahjoub.online باستخدام المفتاح الجديد"""
    
    # ترويسات المصادقة (Headers) - الهيدر المضاف يحل مشكلة "Unable to reach server"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "apollo-require-preflight": "true", # ضروري جداً لتجاوز حظر المتصفح
        "Accept": "application/json",
    }

    # استعلام الـ Mutation المعتمد لرفع المنتجات وربطها بالمورد
    query = """
    mutation CreateProduct($input: ProductInput!, $image: Upload) {
      createProduct(input: $input, image: $image) {
        id
        name
        status
      }
    }
    """
    
    # تجهيز كائن العمليات وربط المنتج بالـ vendor_id الصحيح
    operations = {
        'query': query,
        'variables': {
            'input': {
                'name': name,
                'description': description or "منتج تم رفعه عبر منصة قمرة - محجوب أونلاين",
                'price': float(final_price),
                'status': 'DRAFT', # يظهر كمسودة للمراجعة والتدقيق السيادي
                'currency': 'SAR',
                'vendorId': str(vendor_id) # ربط المنتج بالمورد الحالي في قاعدة البيانات
            },
            'image': None 
        }
    }
    
    # خريطة الربط لرفع الملفات (Multi-part upload)
    map_data = {'0': ['variables.image']}
    
    try:
        # تشكيل طلب Multipart لرفع الصورة والبيانات معاً
        files = {
            'operations': (None, json.dumps(operations), 'application/json'),
            'map': (None, json.dumps(map_data), 'application/json'),
            '0': ('product_image.webp', image_buffer, 'image/webp')
        }
        
        # إرسال الطلب الفعلي
        response = requests.post(GRAPHQL_URL, headers=headers, files=files)
        
        print(f"📡 رد السيرفر: {response.status_code}")
        
        if response.status_code == 200 and "errors" not in response.text:
            print(f"✅ مبروك يا علي! المنتج '{name}' أصبح الآن في متجر محجوب أونلاين.")
            return True, "تم الرفع بنجاح"
        else:
            error_details = response.json().get('errors', [{}])[0].get('message', 'خطأ مجهول')
            print(f"❌ فشل الرفع: {error_details}")
            return False, error_details
            
    except Exception as e:
        print(f"⚠️ خطأ فادح في اتصال الجسر: {e}")
        return False, str(e)
