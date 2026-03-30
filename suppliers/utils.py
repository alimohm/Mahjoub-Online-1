import requests

def sync_to_qumra(product_data):
    api_url = "https://api.qumra.com/v1/products" # رابط الـ API الخاص بقمرة
    api_key = "YOUR_QUMRA_API_KEY" # مفتاح الربط الخاص بمتجرك
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(api_url, json=product_data, headers=headers)
    return response.status_code == 201
