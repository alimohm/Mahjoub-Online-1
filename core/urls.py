from django.contrib import admin
from django.urls import path, include
from suppliers.views import dashboard
from django.shortcuts import redirect

def root_redirect(request):
    return redirect('/login/' if not request.user.is_authenticated else '/dashboard/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', include('django.contrib.auth.urls')),
    path('dashboard/', dashboard, name='dashboard'),
    path('', root_redirect),
]
