from django.contrib import admin
from django.urls import path, include
from suppliers.views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls), #
    path('login/', include('django.contrib.auth.urls')), # تفعيل صفحة الدخول
    path('dashboard/', dashboard, name='dashboard'), # تفعيل لوحة الرفع
    path('', dashboard), # الصفحة الرئيسية
]
