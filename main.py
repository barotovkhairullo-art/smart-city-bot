import time
import schedule
import json
import threading
from history_events import get_tajikistan_history
from weather_service import get_dushanbe_weather
from admin_bot import application
import requests
from datetime import datetime

TELEGRAM_BOT_TOKEN = "8249137825:AAHChjPuHOdL7Y5su0gYpQnwtDZ4ubfXsl0"
CHANNEL_ID = "-1003104338746"
STICKER_ID = "CAACAgIAAxkBAAEPnw5o-adhPImHgSmQpfa-yO9kVk1RxAACwwwAAsVEyEtvpOuf2LbHBDYE"

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def send_sticker():
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendSticker"
        data = {"chat_id": CHANNEL_ID, "sticker": STICKER_ID}
        requests.post(url, data=data)
        print("✅ Стикер отправлен!")
    except:
        print("❌ Ошибка стикера")

def send_daily_report():
    try:
        history_text = get_tajikistan_history()
        weather_text = get_dushanbe_weather()
        
        message = f"📅 ЕЖЕДНЕВНАЯ СВОДКА\n\n"
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

def scheduled_job():
    config = load_config()
    if not config["BOT_ENABLED"]:
        print("⏸️ Бот выключен в настройках")
        return
        
    print(f"\n🔄 Автоматическая отправка в {datetime.now().strftime('%H:%M:%S')}")
    send_sticker()
    time.sleep(1)
    send_daily_report()

def run_admin_bot():
    print("🤖 Запуск админ-бота...")
    application.run_polling()

def main():
    # Загружаем конфигурацию
    config = load_config()
    
    # Настраиваем расписание с учетом UTC+5
    send_hour = config["SEND_HOUR"] - 5
    if send_hour < 0:
        send_hour += 24
        
    schedule.every().day.at(f"{send_hour:02d}:{config['SEND_MINUTE']:02d}").do(scheduled_job)
    
    print("🚀 Бот Умный Город запущен!")
    print(f"⏰ Расписание: каждый день в {config['SEND_HOUR']:02d}:{config['SEND_MINUTE']:02d} по Душанбе")
    print(f"🔧 Статус: {'✅ ВКЛЮЧЕН' if config['BOT_ENABLED'] else '❌ ВЫКЛЮЧЕН'}")
    print("👑 Админ-панель активна!")
    print("📋 Команды: /start в личке с ботом")
    print("🛑 Для остановки нажмите Ctrl+C\n")
    
    # Запускаем админ-бота в отдельном потоке
    bot_thread = threading.Thread(target=run_admin_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Тестовая отправка
    if config["BOT_ENABLED"]:
        print("🔄 Тестовая отправка...")
        send_sticker()
        time.sleep(1)
        send_daily_report()
        print("✅ Тест завершен!\n")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except KeyboardInterrupt:
            print("\n🛑 Бот остановлен")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()