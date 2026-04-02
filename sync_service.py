import os
import requests
import json

GRAPHQL_URL = "https://mahjoub.online/admin/graphql"
API_KEY = str(os.environ.get("QUMRA_ACCESS_TOKEN", "ضع_التوكن_هنا")).strip()
BASE_URL = "https://mahjoub-online-1-production-c824.up.railway.app"

def send_to_qumra_webhook(name, price, description, image_filename=None):
    headers = {
        "Authorization": "Bearer " + API_KEY,
        "Content-Type": "application/json"
    }

    query = """
    mutation CreateProduct($name: String!, $price: Float!, $description: String, $image: String) {
      createProduct(name: $name, price: $price, description: $description, image: $image) {
        _id
        title
      }
    }
    """
    
    variables = {
        "name": str(name),
        "price": float(price),
        "description": str(description),
        "image": (BASE_URL + "/static/uploads/" + str(image_filename)) if image_filename else None
    }

    try:
        json_payload = json.dumps({'query': query, 'variables': variables}, ensure_ascii=False)
        response = requests.post(GRAPHQL_URL, data=json_payload.encode('utf-8'), headers=headers, timeout=30)
        response_data = response.json()

        if response.status_code == 200 and "errors" not in response_data:
            return True
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
