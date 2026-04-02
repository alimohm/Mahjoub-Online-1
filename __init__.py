# ملف التجميع والربط __init__.py

from .database import db, init_db
from .models import Vendor, Product, generate_mah_wallet
from .logic import login_vendor, logout, is_logged_in
from .sync_service import send_to_qumra_webhook

# الآن أي ملف آخر في المشروع يستطيع استدعاء هذه الأدوات بساطة
# مثال: from . import db, Vendor
