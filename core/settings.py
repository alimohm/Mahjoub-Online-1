import os
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-mahjoub-online-key-2026'
DEBUG = True # اجعلها False عند النشر النهائي
ALLOWED_HOSTS = ['*'] # للسماح برابط Railway بالعمل

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'suppliers', # تطبيق الموردين الخاص بك
]

# ربط قاعدة بيانات Railway
DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
}

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
