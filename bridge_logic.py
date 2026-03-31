import requests
from config import Config

def push_to_store(data):
    # بناء استعلام GraphQL لإضافة منتج (Mutation)
    query = """
    mutation createProduct($input: ProductInput!) {
      createProduct(input: $input) {
        product {
          id
          name
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    
    # تجهيز المتغيرات (Variables) مع وضع السعر النهائي والوصف
    variables = {
        "input": {
            "name": data['name'],
            "description": data['description'],
            "regularPrice": float(data['final_price']),
            "status": "DRAFT", # الرفع كمسودة للمراجعة
            "sku": data['wallet'] # ربط رقم المحفظة بالمنتج
        }
    }

    headers = {
        "Authorization": f"Bearer {Config.ACCESS_TOKEN}", # التوثيق المطلوب
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            Config.GRAPHQL_URL,
            json={'query': query, 'variables': variables},
            headers=headers,
            timeout=15
        )
        
        res_data = response.json()
        # التأكد من عدم وجود أخطاء في الـ GraphQL نفسه
        if 'data' in res_data and res_data['data']['createProduct']['product']:
            return True
        else:
            print(f"GraphQL Errors: {res_data.get('errors') or res_data['data']['createProduct']['userErrors']}")
            return False
    except Exception as e:
        print(f"Connection Error: {str(e)}")
        return False
