import requests
from config import Config

def push_to_store(data):
    payload = {
        "event": "topic-product.created",
        "data": {
            "name": data['name'],
            "price": data['final_price'],
            "description": data['description'],
            "image_url": data['image_url'],
            "vendor_wallet": data['wallet'],
            "status": "draft"
        }
    }
    
    headers = {
        "Authorization": f"Bearer {Config.WEBHOOK_SECRET}",
        "Content-Type": "application/json"
    }

    try:
        r = requests.post(Config.WEBHOOK_URL, json=payload, headers=headers, timeout=15)
        return r.status_code in [200, 201, 202]
    except:
        return False
