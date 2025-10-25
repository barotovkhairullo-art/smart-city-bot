import time
import json
import requests
from datetime import datetime
from history_events import get_tajikistan_history
from weather_service import get_dushanbe_weather
from admin_handler import check_admin_messages

TELEGRAM_BOT_TOKEN = "8404371791:AAG-uiZ7Oab4udWZsb5HgijR56dPMPBH9W0"
STICKER_ID = "CAACAgIAAxkBAAEPnw5o-adhPImHgSmQpfa-yO9kVk1RxAACwwwAAsVEyEtvpOuf2LbHBDYE"

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def send_sticker(group_id):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendSticker"
        data = {"chat_id": group_id, "sticker": STICKER_ID}
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print(f"✅ Стикер отправлен в группу {group_id}!")
        else:
            print(f"❌ Ошибка отправки стикера в группу {group_id}")
    except Exception as e:
        print(f"❌ Ошибка стикера: {e}")

def send_daily_report(group_id):
    try:
        history_text = get_tajikistan_history()
        weather_text = get_dushanbe_weather()
        
        message = f"📅 ЕЖЕДНЕВНАЯ СВОДКА\n\n"
        message += history_text + "\n"
        message += weather_text + "\n\n"
        message += "🇹🇯 Государственное унитарное предприятие «Умный город»"
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": group_id, "text": message}
        
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            print(f"✅ Сообщение отправлено в группу {group_id}! Время: {datetime.now().strftime('%H:%M:%S')}")
            return True
        else:
            print(f"❌ Ошибка отправки в группу {group_id}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка формирования отчета: {e}")
        return False

def should_send_now():
    """Проверяет, нужно ли отправлять сообщение сейчас"""
    config = load_config()
    if not config["BOT_ENABLED"]:
        return False
        
    current_time = datetime.now()
    dushanbe_hour = config["SEND_HOUR"]
    dushanbe_minute = config["SEND_MINUTE"]
    
    # Конвертируем время Душанбе в UTC (Душанбе UTC+5)
    utc_hour = (dushanbe_hour - 5) % 24
    
    return (current_time.hour == utc_hour and 
            current_time.minute == dushanbe_minute and
            current_time.second == 0)

def scheduled_job():
    config = load_config()
    if not config["BOT_ENABLED"]:
        print("⏸️ Бот выключен в настройках")
        return
        
    current_time = datetime.now().strftime('%H:%M:%S')
    groups = config.get("GROUP_IDS", [])
    
    print(f"\n🔄 Автоматическая отправка в {current_time}")
    print(f"📢 Отправка в {len(groups)} групп")
    
    for group_id in groups:
        send_sticker(group_id)
        time.sleep(2)
        send_daily_report(group_id)
        time.sleep(1)

def main():
    print("🚀 Бот Умный Город запускается...")
    config = load_config()
    
    dushanbe_hour = config["SEND_HOUR"]
    dushanbe_minute = config["SEND_MINUTE"]
    utc_hour = (dushanbe_hour - 5) % 24
    
    print("✅ Бот успешно запущен!")
    print(f"⏰ Расписание отправки:")
    print(f"   📍 Душанбе: {dushanbe_hour:02d}:{dushanbe_minute:02d} (UTC+5)")
    print(f"   🌐 Сервер: {utc_hour:02d}:{dushanbe_minute:02d} (UTC)")
    print(f"🔧 Статус бота: {'✅ ВКЛЮЧЕН' if config['BOT_ENABLED'] else '❌ ВЫКЛЮЧЕН'}")
    print("👑 Админ-панель активна!")
    
    if config["BOT_ENABLED"]:
        print("\n🔄 Выполняю тестовую отправку...")
        groups = config.get("GROUP_IDS", [])
        for group_id in groups:
            send_sticker(group_id)
            time.sleep(2)
            send_daily_report(group_id)
            time.sleep(1)
        print("✅ Тест завершен!\n")
    
    last_sent_hour = -1
    while True:
        try:
            # Проверяем сообщения админа
            check_admin_messages()
            
            # Проверяем, нужно ли отправить ежедневный отчет
            if should_send_now():
                scheduled_job()
            
            # Обновляем конфигурацию каждую минуту
            current_minute = datetime.now().minute
            if current_minute == 0:
                config = load_config()
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n🛑 Бот остановлен пользователем")
            break
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
