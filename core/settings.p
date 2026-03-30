TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # هذا السطر يخبر Django بمكان المجلد
        'APP_DIRS': True,
        # ... باقي الإعدادات
    },
]
