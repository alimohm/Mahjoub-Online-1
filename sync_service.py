import requests

# بيانات الربط السيادي مع منصة قمرة
# ملاحظة: الـ Store ID هو جزء من الرابط، والـ API Key هو المفتاح السري
API_KEY = "qmr_e235dd03-f398-473f-aa12-79029f05e147" 
WEBHOOK_URL = "https://api.qumra.cloud/v1/products" # الرابط الموحد لإضافة المنتجات

def send_to_qumra_webhook(name, price, description):
    # إعدادات المصادقة (Authorization)
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # تجهيز طرد البيانات (Payload)
    payload = {
        "title": name,
        "price": float(price) if price else 0,
        "description": description,
        "metadata": {
            "origin": "Mahjoub Online",
            "platform": "Smart Market"
        }
    }

    try:
        # إرسال الطلب مع مهلة انتظار 10 ثوانٍ لمنع تعليق السيرفر
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers, timeout=10)
        
        # طباعة النتيجة في سجلات Railway للمراقبة
        print(f"📡 حالة إرسال قمرة: {response.status_code}")
        
        # إذا كان الكود 200 أو 201 فالعملية نجحت
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"❌ فشل الاتصال بقمرة: {e}")
        return False
