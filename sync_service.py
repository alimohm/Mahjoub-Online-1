import os
import requests
import json # أضفنا هذه المكتبة للتأكد من التشفير

GRAPHQL_URL = "https://mahjoub.online/admin/graphql"
API_KEY = os.environ.get("QUMRA_ACCESS_TOKEN", "YOUR_TOKEN")

def send_to_qumra_webhook(name, price, description, image_filename=None):
    BASE_URL = "https://mahjoub-online-1-production-c824.up.railway.app"
    
    # التأكد من أن الترويسات تحتوي فقط على حروف إنجليزية (ASCII)
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    query = """
    mutation CreateNewProduct($input: CreateProductInput!) {
      createProduct(input: $input) {
        id
        title
      }
    }
    """
    
    variables = {
        "input": {
            "title": name,
            "price": float(price),
            "description": description,
            "image": f"{BASE_URL}/static/uploads/{image_filename}" if image_filename else None
        }
    }

    try:
        # التعديل الهام: نستخدم json.dumps لضمان تشفير الحروف العربية بشكل صحيح (UTF-8)
        data_to_send = json.dumps({'query': query, 'variables': variables}, ensure_ascii=False).encode('utf-8')
        
        print(f"🚀 جاري المزامنة السيادية لمنتج: {name}")
        
        response = requests.post(
            GRAPHQL_URL, 
            data=data_to_send, # نرسل البيانات المشفرة يدوياً
            headers=headers, 
            timeout=30
        )
        
        # لعرض الرد الفعلي من قمرة في سجلات Railway
        print(f"📡 رد السيرفر: {response.status_code} - {response.text}")
        
        return response.status_code == 200

    except Exception as e:
        print(f"❌ فشل الإرسال بسبب تشفير النصوص: {e}")
        return False
