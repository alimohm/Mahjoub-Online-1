from django.contrib import admin
from django.urls import path, include
from suppliers.views import dashboard

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('dashboard/', dashboard, name='dashboard'),
    path('', dashboard), # جعل الداشبورد الصفحة الرئيسية بعد الدخول
]
