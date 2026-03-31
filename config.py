import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mahjoub_sovereign_2026')
    # الـ Access Token الخاص بمتجرك
    ACCESS_TOKEN = "qmr_dcbbd1f6-d0a7-43ed-9b4c-4a9394be06b9" 
    # نقطة اتصال GraphQL الصحيحة
    GRAPHQL_URL = "https://mahjoub.online/admin/graphql"
    
    USD_TO_SAR = 3.8
    PROFIT_MARGIN = 1.30
