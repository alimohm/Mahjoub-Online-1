import os
import requests

# إعدادات الربط السيادي - يتم سحبها من متغيرات البيئة في Railway للأمان
# إذا لم تكن موجودة في Railway، سيستخدم القيم الافتراضية بالأسفل
API_KEY = os.environ.get("QUMRA_API_KEY", "qmr_e235dd03-f398-473f-aa12-79029f05e147")
STORE_ID = "qmr_e235dd03-f398-473f-aa12-79029f05e147"

# الرابط المباشر لإضافة المنتجات في متجر قمرة الخاص بك
API_URL = f"https://api.qumra.cloud/v1/stores/{STORE_ID}/products"

# رابط سيرفرك الأساسي في Railway (ضروري لكي تجد قمرة رابط الصورة وتنسخها)
BASE_URL = "https://mahjoub-online-1-production-c824.up.railway.app"

def send_to_qumra_webhook(name, price, description, image_filename=None):
    """
    وظيفة المزامنة: إرسال بيانات المنتج من لوحة محجوب إلى منصة قمرة.
    تدعم إرسال رابط الصورة لكي تظهر في المتجر تلقائياً.
    """
    
    # 1. التأكد من وجود الهوية البرمجية (API Key)
    if not API_KEY:
        print("❌ خطأ: مفتاح الـ API (QUMRA_API_KEY) غير مضبوط في Railway!")
        return False

    # 2. إعدادات الترويسة (Headers) لفتح قفل الأمان في قمرة
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # 3. تجهيز طرد البيانات (Payload)
    payload = {
        "title": name,
        "price": float(price) if price else 0.0,
        "description": description,
        "metadata": {
            "origin": "Mahjoub Online",
            "platform": "Smart Market",
            "sync_version": "2.1"
        }
    }

    # 4. إضافة رابط الصورة إذا كانت موجودة
    if image_filename:
        # نخبر قمرة: "يا قمرة، حملي صورة المنتج من هذا الرابط العام"
        payload["main_image"] = f"{BASE_URL}/static/uploads/{image_filename}"

    try:
        # 5. تنفيذ عملية الإرسال مع مهلة انتظار 25 ثانية (لتفادي الـ Timeout)
        print(f"📡 جاري محاولة مزامنة المنتج '{name}' مع قمرة...")
        response = requests.post(API_URL, json=payload, headers=headers, timeout=25)
        
        # 6. تحليل النتيجة المرتجعة من قمرة
        print(f"📡 استجابة سيرفر قمرة: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print(f"✅ نجحت المزامنة السيادية! المنتج متاح الآن في متجر قمرة.")
            return True
        else:
            # طباعة نص الخطأ لتعرف السبب (مثلاً لو كان السعر غير منطقي أو الاسم مكرر)
            print(f"⚠️ رفضت قمرة الطلب. السبب: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏳ انتهى وقت الانتظار (Timeout). سيرفر قمرة تأخر في الرد.")
        return False
    except Exception as e:
        print(f"❌ فشل الاتصال التقني بقمرة: {e}")
        return False
