
import os
from django.core.wsgi import get_wsgi_application

# تأكد أن 'core.settings' تطابق اسم مجلد إعداداتك
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Gunicorn يبحث عن هذا المتغير 'application' تحديداً
application = get_wsgi_application()
