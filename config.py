import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mahjoub_sovereign_2026')
    # المفتاح الأخير للربط مع المتجر
    MAHJOUB_API_KEY = "qmr_dcbbd1f6-d0a7-43ed-9b4c-4a9394be06b9"
    STORE_URL = "https://mahjoub.online/api/v1/products"
    
    # الثوابت المالية السيادية
    USD_TO_SAR = 3.8
    PROFIT_MARGIN = 1.30  # إضافة 30% تلقائياً
