
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # ربط روابط الموردين
    path('suppliers/', include('suppliers.urls')),
]
