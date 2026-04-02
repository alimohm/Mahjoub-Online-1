import os
import requests

# الرابط المستخرج من واجهة GraphQL في صورتك
GRAPHQL_URL = "https://mahjoub.online/admin/graphql"

# المفتاح الذي أنشأته توكاً (Access Token)
# يفضل وضعه في Railway Environment باسم QUMRA_ACCESS_TOKEN
API_KEY = os.environ.get("QUMRA_ACCESS_TOKEN", "ضع_المفتاح_الجديد_هنا")

def send_to_qumra_webhook(name, price, description, image_filename=None):
    """
    إرسال المنتج عبر GraphQL Mutation (التنسيق المعتمد في قمرة كلاود)
    """
    # رابط سيرفرك في Railway للوصول للصور
    BASE_URL = "https://mahjoub-online-1-production-c824.up.railway.app"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # صياغة الاستعلام (Mutation) لإضافة منتج جديد
    # ملاحظة: قد تختلف مسميات الحقول (Fields) قليلاً حسب توثيق قمرة
    query = """
    mutation CreateNewProduct($input: CreateProductInput!) {
      createProduct(input: $input) {
        id
        title
        price
      }
    }
    """
    
    # تجهيز المتغيرات (Variables)
    variables = {
        "input": {
            "title": name,
            "price": float(price),
            "description": description,
            "image": f"{BASE_URL}/static/uploads/{image_filename}" if image_filename else None
        }
    }

    try:
        print(f"🚀 جاري إرسال المنتج عبر GraphQL: {name}")
        response = requests.post(
            GRAPHQL_URL, 
            json={'query': query, 'variables': variables}, 
            headers=headers, 
            timeout=30 # مهلة أطول لمعالجة طلبات GraphQL
        )
        
        result = response.json()
        
        # التحقق من وجود أخطاء في رد GraphQL
        if "errors" in result:
            print(f"⚠️ خطأ في منطق GraphQL: {result['errors']}")
            return False
            
        if response.status_code == 200:
            print(f"✅ تمت المزامنة السيادية عبر GraphQL بنجاح!")
            return True
        else:
            print(f"❌ فشل الاتصال: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ خطأ تقني غير متوقع: {e}")
        return False
