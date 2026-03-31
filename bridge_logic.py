import requests
from config import Config

def push_to_store(data):
    payload = {
        "api_key": Config.MAHJOUB_API_KEY,
        "product_name": data['name'],
        "price": data['final_price'],
        "description": data['description'],
        "vendor_wallet": data['wallet'],
        "status": "draft" # يظهر كمسودة للمراجعة
    }
    try:
        response = requests.post(Config.STORE_URL, json=payload, timeout=10)
        return response.status_code in [200, 201]
    except:
        return False
