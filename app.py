from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = 'mahjoub_ai_2026' # مفتاح الأمان للمنصة

# إعدادات متجر قمرة
QUMRA_URL = "https://mahjoub.online/admin/graphql"
HEADERS = {"Authorization": "Bearer YOUR_TOKEN"}

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # نظام دخول بسيط (يمكنك ربطه بقاعدة بيانات لاحقاً)
        if request.form['username'] == 'admin' and request.form['password'] == '123':
            session['user'] = 'admin'
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form['p_name']
        price = float(request.form['p_price'])
        final_price = price * 1.40 # إضافة 40% آلياً
        
        # إرسال البيانات لقمرة بذكاء
        query = 'mutation { productCreate(input: { name: "%s", basePrice: %f }) { product { id } } }' % (name, final_price)
        requests.post(QUMRA_URL, json={'query': query}, headers=HEADERS)
        return "تم الرفع بنجاح بالسعر الذكي: " + str(final_price)

    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run()
