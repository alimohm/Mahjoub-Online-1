import os
from pathlib import Path
import dj_database_url

# المسار الأساسي للمشروع
BASE_DIR = Path(__file__).resolve().parent.parent

# إعدادات الأمان
SECRET_KEY = 'django-insecure-mahjoub-smart-market-ai-2026'
DEBUG = False # تعطيل وضع التصحيح للإنتاج
ALLOWED_HOSTS = ['*'] # السماح لجميع النطاقات (Railway)

# التطبيقات المثبتة
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'suppliers', # تطبيق الموردين الخاص بك
]

# الميدل وير (الطبقات الوسيطة)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # الحل السحري لظهور الألوان والتنسيقات
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

# إعدادات القوالب (Templates)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # مسار مجلد الواجهات
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# قاعدة البيانات (الرابط الذي أرسلته من Railway)
DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://postgres:aNAkUjEswZOHdTaWPQdjUlmPCwIaKtWG@hopper.proxy.rlwy.net:26


        # هذا السطر يجعل الملفات "ديناميكية" وغير ثابتة في الذاكرة القديمة
STATICFILES_STORAGE = 'whitenoise.storage.ManifestStaticFilesStorage'
