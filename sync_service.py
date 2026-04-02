import os
import requests
import json

GRAPHQL_URL = "https://mahjoub.online/admin/graphql"

# جلب المفتاح والتأكد من أنه نص إنجليزي سليم
API_KEY = str(os.environ.get("QUMRA_ACCESS_TOKEN", "")).strip()

def send_to_qumra_webhook(name, price, description, image_filename=None):
    """
    إرسال المنتج مع ضمان تشفير UTF-8 للحروف العربية لمنع خطأ latin-1.
    """
    BASE_URL = "https://mahjoub-online-1-production-c824.up.railway.app"
    
    # التأكد من خلو Headers من أي حروف عربية أو مسافات غريبة
    headers = {
        "Authorization": "Bearer " + API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    query = """
    mutation CreateNewProduct($input: CreateProductInput!) {
      createProduct(input: $input) {
        id
        title
        status
      }
    }
    """
    
    variables = {
        "input": {
            "title": str(name),
            "price": float(price),
            "description": str(description),
            "status": "DRAFT",
            "image": (BASE_URL + "/static/uploads/" + str(image_filename)) if image_filename else None
        }
    }

    try:
        # الحل الجذري: تحويل البيانات إلى JSON ثم Encode إلى bytes باستخدام utf-8
        # هذا يمنع requests من محاولة استخدام تشفير latin-1 الافتراضي
        json_payload = json.dumps({'query': query, 'variables': variables}, ensure_ascii=False)
        encoded_payload = json_payload.encode('utf-8')
        
        print("🚀 محاولة إرسال البيانات المشفرة لمنتج: " + str(name))
        
        response = requests.post(
            GRAPHQL_URL, 
            data=encoded_payload, # نرسل الـ bytes مباشرة
            headers=headers, 
            timeout=30
        )
        
        # تحليل الرد
        try:
            response_data = response.json()
            print("📡 رد السيرفر: " + json.dumps(response_data, ensure_ascii=False))
        except:
            print("📡 رد غير مفهوم من السيرفر")

        return response.status_code == 200 and "errors" not in response.text

    except Exception as e:
        # طباعة الخطأ بشكل آمن
        print("❌ خطأ أثناء الإرسال: " + str(e))
        return False
