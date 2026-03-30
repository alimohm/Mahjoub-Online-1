from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, Supplier
from django.contrib.auth.models import User

def supplier_login(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        if not User.objects.filter(username=u).exists():
            messages.error(request, "الحساب غير مسجل في المنصة")
        else:
            user = authenticate(username=u, password=p)
            if user:
                login(request, user)
                return redirect('suppliers:dashboard')
            else:
                messages.error(request, "كلمة المرور خطأ")
    return render(request, 'suppliers/login.html')

@login_required
def supplier_dashboard(request):
    draft_count = Product.objects.filter(supplier=request.user.supplier, status='draft').count()
    return render(request, 'suppliers/dashboard.html', {'draft_count': draft_count})
