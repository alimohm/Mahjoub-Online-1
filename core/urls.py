from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.path),
    # هنا ستضيف روابط الموردين والمنتجات لاحقاً
]
