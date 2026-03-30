import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# الحصول على المسار الرئيسي للمشروع (المكان الذي يوجد فيه manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# إضافة المسار الرئيسي إلى بيئة بايثون لضمان رؤية مجلد core
sys.path.append(str(BASE_DIR))

# التأكد من توجيه Django لملف الإعدادات
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()
