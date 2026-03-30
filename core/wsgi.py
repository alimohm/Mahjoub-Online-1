import os
from django.core.wsgi import get_wsgi_application

# إعداد ملف الإعدادات الافتراضي للمشروع
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# هذا هو المتغير الذي يبحث عنه Gunicorn (يجب أن يكون اسمه application)
application = get_wsgi_application()
