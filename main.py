import time
import schedule
import json
import requests
from datetime import datetime
from history_events import get_tajikistan_history
from weather_service import get_dushanbe_weather
from admin_handler import check_admin_messages

TELEGRAM_BOT_TOKEN = "8249137825:AAHChjPuHOdL7Y5su0gYpQnwtDZ4ubfXsl0"
CHANNEL_ID = "-1003104338746"
STICKER_ID = "CAACAgIAAxkBAAEPnw5o-adhPImHgSmQpfa-yO9kVk1RxAACwwwAAsVEyEtvpOuf2LbHBDYE"

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def send_sticker():
    """Отправляет стикер в канал"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendSticker"
        data = {"chat_id": CHANNEL_ID, "sticker": STICKER_ID}
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("✅ Стикер отправлен!")
        else:
            print("❌ Ошибка отправки стикера")
    except Exception as e:
        print(f"❌ Ошибка стикера: {e}")

def send_daily_report():
    """Отправляет ежедневную сводку в канал"""
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
            print(f"❌ Ошибка отправки: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка формирования отчета: {e}")
        return False

def scheduled_job():
    """Задача по расписанию"""
    config = load_config()
    if not config["BOT_ENABLED"]:
        print("⏸️ Бот выключен в настройках")
        return
        
    current_time = datetime.now().strftime('%H:%M:%S')
    print(f"\n🔄 Автоматическая отправка в {current_time}")
    
    send_sticker()
    time.sleep(2)
    send_daily_report()

def setup_schedule():
    """Настраивает расписание с учетом времени Душанбе"""
    config = load_config()
    
    # Время в Душанбе (UTC+5)
    dushanbe_hour = config["SEND_HOUR"]
    dushanbe_minute = config["SEND_MINUTE"]
    
    # Конвертируем в UTC (для сервера)
    utc_hour = (dushanbe_hour - 5) % 24
    
    schedule_time = f"{utc_hour:02d}:{dushanbe_minute:02d}"
    
    # Очищаем предыдущее расписание
    schedule.clear()
    
    # Устанавливаем новое расписание
    schedule.every().day.at(schedule_time).do(scheduled_job)
    
    return dushanbe_hour, dushanbe_minute, utc_hour

def main():
    """Основная функция"""
    print("🚀 Бот Умный Город запускается...")
    
    # Настраиваем расписание
    dushanbe_hour, dushanbe_minute, utc_hour = setup_schedule()
    config = load_config()
    
    print("✅ Бот успешно запущен!")
    print(f"⏰ Расписание отправки:")
    print(f"   📍 Душанбе: {dushanbe_hour:02d}:{dushanbe_minute:02d} (UTC+5)")
    print(f"   🌐 Сервер: {utc_hour:02d}:{dushanbe_minute:02d} (UTC)")
    print(f"🔧 Статус бота: {'✅ ВКЛЮЧЕН' if config['BOT_ENABLED'] else '❌ ВЫКЛЮЧЕН'}")
    print("👑 Админ-панель активна!")
    print("\n📋 Команды админа:")
    print("   /start - показать все команды")
    print("   /settime ЧАС МИНУТА - изменить время отправки")
    print("   /time - текущее время отправки")
    print("   /addevent ДД.ММ Событие - добавить историческое событие")
    print("   /test - тестовая отправка в канал")
    print("   /enable /disable - вкл/выкл бота")
    print("\n🛑 Для остановки нажмите Ctrl+C")
    
    # Тестовая отправка при запуске
    if config["BOT_ENABLED"]:
        print("\n🔄 Выполняю тестовую отправку...")
        send_sticker()
        time.sleep(2)
        send_daily_report()
        print("✅ Тест завершен!\n")
    
    # Основной цикл
    while True:
        try:
            schedule.run_pending()
            
            # Проверяем сообщения от админов каждые 5 секунд
            check_admin_messages()
            
            # Обновляем расписание каждую минуту (на случай изменения времени)
            current_second = datetime.now().second
            if current_second < 5:  # В начале каждой минуты
                setup_schedule()
            
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\n🛑 Бот остановлен пользователем")
            break
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()