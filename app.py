from flask import Flask
from database import init_db
from config import Config

app = Flask(__name__)
# تحميل الإعدادات لإنهاء خطأ SQLALCHEMY_DATABASE_URI
app.config.from_object(Config)

init_db(app)

# ... باقي المسارات (login_view, etc.)


@app.route('/login', methods=['GET', 'POST'])
def lv():
    if 'v_id' in session: return redirect(url_for('db_v'))
    
    if request.method == 'POST':
        # إرسال اليوزر (u) والباسورد (p) للمنطق
        res = logic.do_auth(request.form.get('username'), request.form.get('password'))
        
        if res['status']:
            session.update({'v_id': res['user'].id, 'name': res['user'].owner_name})
            return redirect(url_for('db_v'))
        
        # تمرير رسالة الخطأ المخصصة للواجهة
        flash(res['msg'], "error")
        
    return render_template('login.html')
