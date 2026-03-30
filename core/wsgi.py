import os
import sys
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# إضافة المسار الرئيسي لذاكرة بايثون
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

try:
    application = get_wsgi_application()
except Exception as e:
    print(f"WSGI Critical Error: {e}")
    raise
