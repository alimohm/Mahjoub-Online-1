import requests
import json
import hmac
import hashlib
from config import Config

def push_to_store(data):
    # تجهيز البيانات النهائية بعد الحسبة المالية
    payload = {
        "event": "product.create",
        "data": {
            "name": data['name'],
            "price": data['final_price'],
            "description": data['description'],
            "vendor_wallet": data['wallet'],
            "status": "draft", # النشر كمسودة للمراجعة
            "currency": "SAR"
        }
    }
    
    # تحويل البيانات لنص JSON
    payload_json = json.dumps(payload)
    
    # توقيع الطلب لزيادة الأمان (Signature) ليعرف المتجر أنه منك
    signature = hmac.new(
        Config.WEBHOOK_SECRET.encode(),
        payload_json.encode(),
        hashlib.sha256
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-Qamrah-Signature": signature,
        "User-Agent": "Qamrah-Cloud-Webhook-Bridge"
    }

    try:
        # إرسال البيانات فوراً دون انتظار تعقيدات الـ GraphQL
        response = requests.post(
            Config.WEBHOOK_URL,
            data=payload_json,
            headers=headers,
            timeout=10
        )
        
        # الويب هوك الناجح عادة يعيد 200 أو 202 (Accepted)
        return response.status_code in [200, 201, 202]
    except:
        return False
