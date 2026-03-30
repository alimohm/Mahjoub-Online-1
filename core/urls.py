from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # تغيير مسار الإدارة التقليدي إلى Dashboard
    path('dashboard/', admin.site.name == 'Mahjoub Online Dashboard'), 
    path('admin/', admin.site.urls), # يمكنك تركها أو حذفها
    
    # مسارات نظام الموردين والمحفظة الرقمية
    path('suppliers/', include('suppliers.urls')), 
]
