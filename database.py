with app.app_context():
        try:
            # استخدام SQL مباشر لتنفيذ الحذف المتسلسل (CASCADE)
            # هذا سيحذف جدول vendor وأي قيود مرتبطة به في الجداول الأخرى
            db.session.execute(db.text('DROP TABLE IF EXISTS vendor CASCADE;'))
            db.session.commit()
            
            # الآن نقوم بإنشاء الجداول بالهيكل الجديد
            db.create_all()
            
            # إنشاء حسابك 'ali' بالهوية والبادئة الجديدة MAH
            if not Vendor.query.filter_by(username='ali').first():
                new_v = Vendor(
                    username='ali',
                    password='123',
                    phone='77xxxxxxx',
                    owner_name='علي محجوب',
                    brand_name='محجوب أونلاين',
                    wallet_address=generate_mah_wallet()
                )
                db.session.add(new_v)
                db.session.commit()
                print("--- تم إنشاء الهيكل الملكي وحساب علي بنجاح ---")
                
        except Exception as e:
            db.session.rollback()
            print(f"خطأ أثناء تحديث القاعدة: {e}")
