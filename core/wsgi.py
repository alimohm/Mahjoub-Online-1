import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# إجبار بايثون على رؤية المجلد الرئيسي للمشروع
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()
