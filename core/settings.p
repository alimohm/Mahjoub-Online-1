
# اجعلها False عند النشر النهائي، لكن اتركها True الآن لتكتشف الأخطاء
DEBUG = True 

# هذا السطر ضروري جداً لكي يقبل السيرفر طلبات الدخول
ALLOWED_HOSTS = ['*'] 

# أضف WhiteNoise للتعامل مع الملفات الساكنة (CSS/JS)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # أضف هذا السطر هنا
    # ... باقي الأسطر
]
