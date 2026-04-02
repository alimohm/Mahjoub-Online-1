import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

# 1. استيراد الإعدادات
from config import Config

# 2. استيراد قاعدة البيانات من database.py
from database import db, init_db

# 3. استيراد الجداول من مكانها الصحيح models.py
from models import Product, Vendor 

# 4. استيراد المنطق والخدمات
from logic import login_vendor, logout, is_logged_in
from sync_service import send_to_qumra_webhook
