import requests
import time
from datetime import datetime

# ТВОИ ДАННЫЕ
TELEGRAM_BOT_TOKEN = "8249137825:AAHChjPuHOdL7Y5su0gYpQnwtDZ4ubfXsl0"
CHANNEL_ID = "-1003104338746"
STICKER_ID = "CAACAgIAAxkBAAEPnw5o-adhPImHgSmQpfa-yO9kVk1RxAACwwwAAsVEyEtvpOuf2LbHBDYE"

def send_sticker():
    """Отправляет стикер"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendSticker"
        data = {"chat_id": CHANNEL_ID, "sticker": STICKER_ID}
        requests.post(url, data=data)
        print("✅ Стикер отправлен!")
    except:
        print("❌ Ошибка стикера")

def send_daily_report(history_text, weather_text):
    """Отправляет сообщение"""
    try:
        today = datetime.now().strftime("%d.%m.%Y")
        
        message = f"📅 ЕЖЕДНЕВНАЯ СВОДКА НА {today}\n\n"
        message += history_text + "\n"
        message += weather_text + "\n\n"
        message += "📖 Государственное унитарное предприятие «Умный город»"
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHANNEL_ID, "text": message}
        
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            print(f"✅ Сообщение отправлено! Время: {datetime.now().strftime('%H:%M:%S')}")
            return True
        else:
            print(f"❌ Ошибка: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False