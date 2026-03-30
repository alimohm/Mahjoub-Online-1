import os
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "mahjoub_online_2026"

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

if __name__ == "__main__":
    # هذا السطر ضروري جداً لـ Railway ليتعرف على المنفذ (Port)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
