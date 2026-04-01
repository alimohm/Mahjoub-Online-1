import os
from flask import Flask, render_template, request, redirect, url_for
from config import Config
from database import db, init_db
from logic import login_vendor, logout, is_logged_in

app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

@app.route('/')
def login_page():
    if is_logged_in(): return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def do_login():
    """معالجة الدخول وحل مشكلة Method Not Allowed"""
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')
        if login_vendor(user, pw):
            return redirect(url_for('dashboard'))
    return redirect(url_for('login_page'))

@app.route('/dashboard')
def dashboard():
    if not is_logged_in(): return redirect(url_for('login_page'))
    return render_template('dashboard.html')

@app.route('/logout')
def logout_route():
    return logout()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
