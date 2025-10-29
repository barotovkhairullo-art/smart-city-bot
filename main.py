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
            return True
        else:
            print(f"❌ Ошибка отправки стикера в группу {group_id}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка стикера: {e}")
        return False

def get_work_time_countdown():
    """Получает обратный отсчет до начала/окончания рабочего дня"""
    now = datetime.now()
    
    # Рабочее время с 8:00 до 17:00
    work_start = now.replace(hour=8, minute=0, second=0, microsecond=0)
    work_end = now.replace(hour=17, minute=0, second=0, microsecond=0)
    
    # Если сейчас до начала рабочего дня
    if now < work_start:
        time_left = work_start - now
        hours = time_left.seconds // 3600
        minutes = (time_left.seconds % 3600) // 60
        return f"⏳ До начала рабочего дня: {hours:02d}:{minutes:02d}"
    
    # Если сейчас рабочее время
    elif work_start <= now <= work_end:
        time_left = work_end - now
        hours = time_left.seconds // 3600
        minutes = (time_left.seconds % 3600) // 60
        return f"⏳ До конца рабочего дня: {hours:02d}:{minutes:02d}"
    
    # Если рабочий день уже закончился
    else:
        # Считаем до начала следующего рабочего дня
        tomorrow = now.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)
        time_left = tomorrow - now
        hours = time_left.seconds // 3600
        minutes = (time_left.seconds % 3600) // 60
        return f"⏳ До начала рабочего дня: {hours:02d}:{minutes:02d}"

def send_daily_report(group_id):
    try:
        history_text = get_tajikistan_history()
        weather_text = get_dushanbe_weather()
        
        # Получаем обратный отсчет времени работы
        countdown_text = get_work_time_countdown()
        
        message = f"📅 ЕЖЕДНЕВНАЯ СВОДКА\n\n"
        message += history_text + "\n\n"
        message += weather_text + "\n\n"
        message += "🏢 Государственное унитарное предприятие «Умный город»\n"
        message += "🕐 Время работы: 8:00 - 17:00\n"
        message += countdown_text + "\n\n"
        message += "🇹🇯"
        
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
    
    # Душанбе UTC+5, сервер UTC
    # Получаем текущее время Душанбе
    current_dushanbe_hour = (current_time.hour + 5) % 24
    current_dushanbe_minute = current_time.minute
    
    # Отладочная информация каждые 30 секунд
    if current_time.second % 30 == 0:
        print(f"🕐 Проверка времени: Душанбе {current_dushanbe_hour:02d}:{current_dushanbe_minute:02d} | Ожидаем: {dushanbe_hour:02d}:{dushanbe_minute:02d}")
    
    # Проверяем совпадает ли текущее время Душанбе с временем отправки
    return (current_dushanbe_hour == dushanbe_hour and 
            current_dushanbe_minute == dushanbe_minute)

def scheduled_job():
    config = load_config()
    if not config["BOT_ENABLED"]:
        print("⏸️ Бот выключен в настройках")
        return
        
    current_time = datetime.now().strftime('%H:%M:%S')
    groups = config.get("GROUP_IDS", [])
    
    print(f"\n🎯 АВТОМАТИЧЕСКАЯ ОТПРАВКА в {current_time}")
    print(f"📢 Отправка в {len(groups)} групп")
    
    success_count = 0
    for group_id in groups:
        if send_sticker(group_id):
            time.sleep(2)
            if send_daily_report(group_id):
                success_count += 1
        time.sleep(1)
    
    print(f"✅ Успешно отправлено в {success_count}/{len(groups)} групп")

def test_bot_connection():
    """Проверка соединения с Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Связь с Telegram API установлена")
            print(f"🤖 Бот: {data['result']['first_name']} (@{data['result']['username']})")
            return True
        else:
            print(f"❌ Ошибка связи с Telegram: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к Telegram: {e}")
        return False

def force_send_test():
    """Принудительная отправка для теста"""
    print("\n" + "="*50)
    print("🚨 ТЕСТОВАЯ ОТПРАВКА ПО КОМАНДЕ")
    print("="*50)
    
    config = load_config()
    groups = config.get("GROUP_IDS", [])
    
    if not groups:
        print("❌ Нет групп для отправки")
        return
    
    success_count = 0
    for group_id in groups:
        print(f"\n📤 Отправка в группу: {group_id}")
        if send_sticker(group_id):
            time.sleep(2)
            if send_daily_report(group_id):
                success_count += 1
        time.sleep(1)
    
    print(f"\n📊 Итог теста: успешно в {success_count}/{len(groups)} групп")

def check_current_time():
    """Проверка текущего времени"""
    current_time = datetime.now()
    config = load_config()
    dushanbe_hour = config["SEND_HOUR"]
    dushanbe_minute = config["SEND_MINUTE"]
    
    current_dushanbe_hour = (current_time.hour + 5) % 24
    
    print(f"\n🕐 ТЕКУЩЕЕ ВРЕМЯ:")
    print(f"   Сервер (UTC): {current_time.hour:02d}:{current_time.minute:02d}:{current_time.second:02d}")
    print(f"   Душанбе (UTC+5): {current_dushanbe_hour:02d}:{current_time.minute:02d}")
    print(f"   Отправка запланирована на:")
    print(f"   - Душанбе: {dushanbe_hour:02d}:{dushanbe_minute:02d}")

def main():
    print("🚀 Бот Умный Город запускается...")
    print("="*50)
    
    # Проверка соединения с Telegram
    if not test_bot_connection():
        print("❌ Не удалось подключиться к Telegram. Проверьте токен бота.")
        return
    
    config = load_config()
    
    dushanbe_hour = config["SEND_HOUR"]
    dushanbe_minute = config["SEND_MINUTE"]
    
    print(f"\n✅ Бот успешно запущен!")
    print(f"⏰ РАСПИСАНИЕ ОТПРАВКИ:")
    print(f"   📍 Душанбе: {dushanbe_hour:02d}:{dushanbe_minute:02d} (UTC+5)")
    print(f"🔧 Статус бота: {'✅ ВКЛЮЧЕН' if config['BOT_ENABLED'] else '❌ ВЫКЛЮЧЕН'}")
    print(f"👥 Групп для рассылки: {len(config.get('GROUP_IDS', []))}")
    print("👑 Админ-панель активна!")
    
    # Проверка текущего времени
    check_current_time()
    
    if config["BOT_ENABLED"]:
        print(f"\n🔄 Выполняю тестовую отправку...")
        groups = config.get("GROUP_IDS", [])
        success_count = 0
        for group_id in groups:
            print(f"\n📤 Тест в группу: {group_id}")
            if send_sticker(group_id):
                time.sleep(2)
                if send_daily_report(group_id):
                    success_count += 1
            time.sleep(1)
        print(f"\n✅ Тест завершен! Успешно: {success_count}/{len(groups)} групп")
    
    print(f"\n{'='*50}")
    print("⏳ Ожидание времени для автоматической отправки...")
    print("Для принудительной отправки напишите боту /test")
    print("="*50)
    
    last_minute = -1
    while True:
        try:
            current_time = datetime.now()
            
            # Проверяем сообщения админа каждую секунду
            check_admin_messages()
            
            # Логируем смену минуты
            if current_time.minute != last_minute:
                last_minute = current_time.minute
                current_dushanbe_hour = (current_time.hour + 5) % 24
                print(f"🕐 Текущее время: {current_time.hour:02d}:{current_time.minute:02d} UTC (Душанбе: {current_dushanbe_hour:02d}:{current_time.minute:02d}) - Ожидаем: {dushanbe_hour:02d}:{dushanbe_minute:02d}")
            
            # Проверяем, нужно ли отправить ежедневный отчет
            if should_send_now():
                print(f"\n🎯 ВРЕМЯ ОТПРАВКИ НАСТУПИЛО! {current_time.strftime('%H:%M:%S')} UTC")
                scheduled_job()
                print(f"\n✅ Отправка завершена. Следующая - завтра в {dushanbe_hour:02d}:{dushanbe_minute:02d} Душанбе")
                # Ждем 60 секунд чтобы не отправить дважды в одну минуту
                time.sleep(60)
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n🛑 Бот остановлен пользователем")
            break
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
