from config import Config

def calculate_final_price(raw_price, currency):
    try:
        price = float(raw_price)
        # تحويل الدولار للريال
        base_price = price * Config.USD_TO_SAR if currency == "USD" else price
        # إضافة عمولة 30%
        return round(base_price * Config.PROFIT_MARGIN, 2)
    except:
        return 0
