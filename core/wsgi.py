import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# الحصول على المسار المطلق للمجلد الحالي وإضافته لـ sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# تحديد ملف الإعدادات
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()
