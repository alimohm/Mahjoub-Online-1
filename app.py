<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>دخول | محجوب أونلاين</title>
    <style>
        body { margin: 0; display: flex; height: 100vh; font-family: 'Cairo', sans-serif; background: #0a001a; color: white; }
        .left-side { flex: 1; background: #fff; color: #333; display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 40px; }
        .right-side { flex: 1; background: #4b0082; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 20px; }
        .login-input { width: 80%; padding: 15px; margin: 10px 0; border: 1px solid #ddd; border-radius: 10px; font-size: 16px; }
        .btn-login { width: 80%; padding: 15px; background: #4b0082; color: #fff; border: none; border-radius: 10px; cursor: pointer; font-weight: bold; font-size: 18px; }
        .feature-box { background: rgba(255,255,255,0.1); padding: 15px; margin: 8px; border-radius: 10px; width: 75%; display: flex; align-items: center; font-size: 14px; border: 1px solid rgba(255,255,255,0.2); }
        .logo { width: 120px; filter: brightness(0) invert(1); margin-bottom: 20px; }
        .alert { color: red; margin-bottom: 15px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="left-side">
        <h2 style="color: #4b0082;">تسجيل الدخول</h2>
        <p>مرحباً بك في نظامك الإداري الملكي</p>
        
        {% with messages = get_flashed_messages() %}
          {% if messages %}<div class="alert">{{ messages[0] }}</div>{% endif %}
        {% endwith %}

        <form method="POST" style="width: 100%; text-align: center;">
            <input type="text" name="username" class="login-input" placeholder="اسم المستخدم" required>
            <input type="password" name="password" class="login-input" placeholder="كلمة المرور" required>
            <button type="submit" class="btn-login">دخول للمنصة</button>
        </form>
    </div>
    <div class="right-side">
        <img src="https://cdn.qumra.cloud/media/67f7f6d5f0b82f44a47bf845/1770229315912-117966978.webp" class="logo">
        <h1>محجوب أونلاين</h1>
        <p style="opacity: 0.8;">قوة اللامركزية وحوكمة سلاسل الإمداد</p>
        <div class="feature-box">🛡️ حوكمة رقمية بنظام لامركزي متطور</div>
        <div class="feature-box">📦 إدارة سلاسل الإمداد والربط التلقائي</div>
        <div class="feature-box">📈 أدوات ذكية لنمو علامتك التجارية</div>
    </div>
</body>
</html>
