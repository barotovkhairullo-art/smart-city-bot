import time
import schedule
from datetime import datetime
from history_events import get_tajikistan_history
from weather_service import get_dushanbe_weather

# ТВОИ ДАННЫЕ
TELEGRAM_BOT_TOKEN = "8249137825:AAHChjPuHOdL7Y5su0gYpQnwtDZ4ubfXsl0"
CHANNEL_ID = "-1003104338746"
STICKER_ID = "CAACAgIAAxkBAAEPnw5o-adhPImHgSmQpfa-yO9kVk1RxAACwwwAAsVEyEtvpOuf2LbHBDYE"

# НАСТРОЙКА ВРЕМЕНИ ОТПРАВКИ
SEND_HOUR = 17    # ← ИЗМЕНИ ЧАСЫ (0-23)
SEND_MINUTE = 0   # ← ИЗМЕНИ МИНУТЫ (0-59)

def send_sticker():
    """Отправляет стикер"""
    try:
        import requests
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendSticker"
        data = {"chat_id": CHANNEL_ID, "sticker": STICKER_ID}
        requests.post(url, data=data)
        print("✅ Стикер отправлен!")
    except:
        print("❌ Ошибка стикера")

def send_daily_report():
    """Отправляет сообщение"""
    try:
        import requests
        today = datetime.now().strftime("%d.%m.%Y")
        
        # Получаем данные из отдельных файлов
        history_text = get_tajikistan_history()
        weather_text = get_dushanbe_weather()
        
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

def scheduled_job():
    """Запланированная отправка"""
    print(f"\n🔄 Автоматическая отправка в {datetime.now().strftime('%H:%M:%S')}")
    send_sticker()
    time.sleep(1)
    send_daily_report()

def main():
    # Настраиваем расписание
    schedule.every().day.at(f"{SEND_HOUR:02d}:{SEND_MINUTE:02d}").do(scheduled_job)
    
    print("🚀 Бот Умный Город запущен!")
    print(f"⏰ Расписание: каждый день в {SEND_HOUR:02d}:{SEND_MINUTE:02d}")
    print("📍 Группа: -1003104338746")
    print("📁 Файлы разделены:")
    print("   - history_events.py - исторические события")
    print("   - weather_service.py - погода")
    print("   - main.py - главный файл")
    print("🛑 Для остановки нажмите Ctrl+C\n")
    
    # Тестовая отправка
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