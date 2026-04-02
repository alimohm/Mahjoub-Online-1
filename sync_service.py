{% extends "layout.html" %}

{% block title %}رفع منتج جديد | محجوب أونلاين{% endblock %}

{% block content %}
<div class="upload-container" style="max-width: 900px; margin: 0 auto; padding: 20px;">
    
    <div class="page-header" style="margin-bottom: 25px; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h2 style="margin: 0; color: var(--main-p-color); font-size: 24px; font-weight: 800;">رفع منتج جديد للسوق</h2>
            <p style="margin: 5px 0; color: #7f8c8d; font-size: 14px;">أدرج منتجاتك الآن في سلسلة الإمداد الرقمية لمستودعات محجوب أونلاين.</p>
        </div>
        <a href="{{ url_for('dashboard') }}" style="text-decoration: none; color: #7f8c8d; font-size: 14px; display: flex; align-items: center;">
            <i class="fas fa-arrow-right" style="margin-left: 8px;"></i> العودة للوحة التحكم
        </a>
    </div>

    <div class="card" style="background: white; padding: 40px; border-radius: 24px; border: 1px solid var(--border-color); box-shadow: 0 10px 30px rgba(0,0,0,0.05);">
        <form id="productForm" action="/add_product" method="POST" enctype="multipart/form-data">
            
            <div class="form-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
                
                <div class="inputs-side">
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; font-weight: 700; margin-bottom: 10px; color: #2c3e50;">اسم المنتج</label>
                        <input type="text" name="name" id="p_name" placeholder="مثلاً: هاتف جلكسي S24" required 
                               style="width: 100%; padding: 14px; border-radius: 12px; border: 1px solid #e0e0e0; font-family: 'Cairo'; outline: none; transition: 0.3s;">
                    </div>

                    <div style="margin-bottom: 20px;">
                        <label style="display: block; font-weight: 700; margin-bottom: 10px; color: #2c3e50;">السعر (MAH)</label>
                        <input type="number" name="price" step="0.01" placeholder="0.00" required
                               style="width: 100%; padding: 14px; border-radius: 12px; border: 1px solid #e0e0e0; outline: none;">
                    </div>
                </div>

                <div class="upload-side">
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; font-weight: 700; margin-bottom: 10px; color: #2c3e50;">صورة المنتج</label>
                        <div id="dropZone" style="border: 2px dashed #cbd5e0; padding: 25px; border-radius: 18px; text-align: center; background: #f8fafc; position: relative; transition: 0.3s; height: 165px; display: flex; align-items: center; justify-content: center; flex-direction: column;">
                            <img id="imgPreview" src="#" alt="Preview" style="display: none; max-width: 100%; max-height: 120px; border-radius: 10px; object-fit: contain;">
                            <div id="uploadContent">
                                <i class="fas fa-cloud-upload-alt" style="font-size: 35px; color: var(--main-p-color); margin-bottom: 10px;"></i>
                                <p style="font-size: 13px; color: #64748b; font-weight: 600;">اسحب الصورة هنا أو اضغط للرفع</p>
                            </div>
                            <input type="file" name="image" id="imageInput" accept="image/*" required 
                                   style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; opacity: 0; cursor: pointer;">
                        </div>
                    </div>
                </div>

            </div>

            <div style="margin-top: 10px;">
                <label style="display: block; font-weight: 700; margin-bottom: 10px; color: #2c3e50;">وصف المنتج</label>
                <textarea name="description" rows="4" placeholder="اكتب تفاصيل المنتج الفنية هنا..." 
                          style="width: 100%; padding: 14px; border-radius: 12px; border: 1px solid #e0e0e0; font-family: 'Cairo'; resize: none; outline: none;"></textarea>
            </div>

            <hr style="margin: 30px 0; border: 0; border-top: 1px solid #f1f5f9;">

            <div style="display: flex; justify-content: flex-end; align-items: center; gap: 15px;">
                <span id="statusMsg" style="font-size: 13px; color: #64748b; display: none;">جاري معالجة البيانات...</span>
                <button type="submit" id="submitBtn" style="background: var(--main-p-color); color: white; border: none; padding: 15px 45px; border-radius: 14px; font-weight: 700; cursor: pointer; font-family: 'Cairo'; transition: 0.4s; display: flex; align-items: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                    <span id="btnIcon"><i class="fas fa-check-circle" style="margin-left: 10px;"></i></span>
                    <span id="btnText">تأكيد الرفع والمزامنة</span>
                    <span id="btnLoader" style="display: none;">
                        <i class="fas fa-spinner fa-spin" style="margin-left: 10px;"></i> جاري المزامنة مع قمرة...
                    </span>
                </button>
            </div>
        </form>
    </div>
</div>

<script>
    // تحسينات المعاينة والتحقق من الملف
    const imageInput = document.getElementById('imageInput');
    const imgPreview = document.getElementById('imgPreview');
    const uploadContent = document.getElementById('uploadContent');
    const dropZone = document.getElementById('dropZone');

    imageInput.onchange = function() {
        const [file] = this.files;
        if (file) {
            // التحقق من الحجم (5 ميجابايت كحد أقصى)
            if (file.size > 5 * 1024 * 1024) {
                alert("❌ عذراً يا علي، حجم الصورة كبير جداً (الأقصى 5MB)");
                this.value = "";
                return;
            }
            imgPreview.src = URL.createObjectURL(file);
            imgPreview.style.display = 'block';
            uploadContent.style.display = 'none';
            dropZone.style.borderColor = 'var(--main-p-color)';
            dropZone.style.background = '#eff6ff';
        }
    };

    // منع الإرسال المتكرر وتحسين شكل زر التحميل
    document.getElementById('productForm').onsubmit = function() {
        const btn = document.getElementById('submitBtn');
        const text = document.getElementById('btnText');
        const icon = document.getElementById('btnIcon');
        const loader = document.getElementById('btnLoader');
        const statusMsg = document.getElementById('statusMsg');

        btn.disabled = true;
        btn.style.opacity = '0.8';
        btn.style.transform = 'scale(0.98)';
        
        text.style.display = 'none';
        icon.style.display = 'none';
        loader.style.display = 'inline-block';
        statusMsg.style.display = 'inline-block';
    };
</script>
{% endblock %}
