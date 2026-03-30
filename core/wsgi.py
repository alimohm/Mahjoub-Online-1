import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# الحصول على المسار المطلق للمجلد الرئيسي
BASE_DIR = Path(__file__).resolve().parent.parent
# إضافته إلى قائمة البحث الخاصة ببايثون
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()
