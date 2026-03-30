
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User

def supplier_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 1. التحقق أولاً هل المستخدم موجود أصلاً في قاعدة البيانات؟
        user_exists = User.objects.filter(username=username).exists()

        if not user_exists:
            messages.error(request, "هذا الحساب غير مسجل في المنصة.")
            return render(request, 'suppliers/login.html')

        # 2. إذا كان موجوداً، نحاول التحقق من كلمة المرور
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"أهلاً بك مجدداً في سوقك الذكي")
            return redirect('suppliers:dashboard')
        else:
            # الحساب موجود ولكن كلمة المرور خطأ
            messages.error(request, "كلمة المرور التي أدخلتها غير صحيحة.")
    
    return render(request, 'suppliers/login.html')



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Product  # استيراد نموذج المنتج من نفس المجلد

@login_required
def supplier_dashboard(request):
    # حساب المنتجات التي حالتها مسودة (Draft) والخاصة بالمورد الحالي فقط
    draft_count = Product.objects.filter(supplier=request.user.supplier, status='draft').count()
    
    context = {
        'draft_count': draft_count,
    }
    return render(request, 'suppliers/dashboard.html', context)
