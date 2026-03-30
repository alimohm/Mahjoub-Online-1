
from django.urls import path
from . import views

app_name = 'suppliers'

urlpatterns = [
    # رابط صفحة الدخول: سيصبح your-domain.com/suppliers/login/
    path('login/', views.supplier_login, name='login'),
]
