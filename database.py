import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

db = SQLAlchemy()

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    wallet_address = db.Column(db.String(255), unique=True)
    brand_name = db.Column(db.String(120))

def init_db(app):
    """ربط المحرك بالقاعدة في Railway"""
    db.init_app(app)
    with app.app_context():
        try:
            db.create_all()
            # إضافة حسابك 'ali' تلقائياً إذا لم يكن موجوداً
            if not Vendor.query.filter_by(username='ali').first():
                from database import generate_mq_wallet # استيراد داخلي لمنع التداخل
                new_v = Vendor(
                    username='ali',
                    password='123',
                    brand_name='محجوب أونلاين',
                    wallet_address='MQ-ALIMAHJOUB2026'
                )
                db.session.add(new_v)
                db.session.commit()
                print("✅ تم إنشاء حساب الأدمن 'ali' بنجاح.")
        except Exception as e:
            print(f"❌ خطأ في ربط القاعدة: {e}")
