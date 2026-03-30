from django.urls import path, include
from suppliers.views import dashboard

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('dashboard/', dashboard, name='dashboard'),
    path('', dashboard), # الصفحة الرئيسية
]
