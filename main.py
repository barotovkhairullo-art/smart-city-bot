import time
import schedule
from history_events import get_tajikistan_history
from weather_service import get_dushanbe_weather
from telegram_bot import send_sticker, send_daily_report

# НАСТРОЙКА ВРЕМЕНИ ОТПРАВКИ
SEND_HOUR = 10    # ← СТАВЬ ЧАСЫ КАК ХОЧЕШЬ (10)
SEND_MINUTE = 58  # ← СТАВЬ МИНУТЫ КАК ХОЧЕШЬ (45)

# АВТОМАТИЧЕСКИ ПЕРЕВОДИМ ВРЕМЯ ДУШАНБЕ → UTC
SEND_HOUR = SEND_HOUR - 5  # Душанбе UTC+5
if SEND_HOUR < 0:
    SEND_HOUR = SEND_HOUR + 24

def scheduled_job():
    """Запланированная отправка"""
    from datetime import datetime
    print(f"\n🔄 Автоматическая отправка в {datetime.now().strftime('%H:%M:%S')}")
    
    # Получаем данные из отдельных модулей
    history_text = get_tajikistan_history()
    weather_text = get_dushanbe_weather()
    
    # Отправляем сообщение
    send_sticker()
    time.sleep(1)
    send_daily_report(history_text, weather_text)

def main():
    # Настраиваем расписание
    schedule.every().day.at(f"{SEND_HOUR:02d}:{SEND_MINUTE:02d}").do(scheduled_job)
    
    print("🚀 Бот Умный Город запущен!")
    print(f"⏰ Расписание: каждый день в 10:45 по Душанбе")
    print(f"📍 Серверное время: {SEND_HOUR:02d}:{SEND_MINUTE:02d} UTC")
    print("📍 Группа: -1003104338746")
    print("📁 Файлы разделены:")
    print("   - history_events.py - исторические события")
    print("   - weather_service.py - погода")
    print("   - telegram_bot.py - отправка в Telegram")
    print("   - main.py - главный файл")
    print("🛑 Для остановки нажмите Ctrl+C\n")
    
    # Тестовая отправка
    print("🔄 Тестовая отправка...")
    history_text = get_tajikistan_history()
    weather_text = get_dushanbe_weather()
    send_sticker()
    time.sleep(1)
    send_daily_report(history_text, weather_text)
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

