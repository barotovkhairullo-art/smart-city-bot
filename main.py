import time
import json
import requests
import random
from datetime import datetime, timedelta
from history_events import get_tajikistan_history
from weather_service import get_dushanbe_weather
from admin_handler import check_admin_messages

TELEGRAM_BOT_TOKEN = "8404371791:AAG-uiZ7Oab4udWZsb5HgijR56dPMPBH9W0"
STICKER_ID = "CAACAgIAAxkBAAEPnw5o-adhPImHgSmQpfa-yO9kVk1RxAACwwwAAsVEyEtvpOuf2LbHBDYE"

# Хранилище для ID последних сообщений
last_message_ids = {}

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

def get_dushanbe_time():
    """Получает текущее время Душанбе (UTC+5)"""
    utc_now = datetime.utcnow()
    dushanbe_time = utc_now + timedelta(hours=5)
    return dushanbe_time

def get_work_time_countdown():
    """Получает обратный отсчет до начала/окончания рабочего дня в Душанбе"""
    dushanbe_now = get_dushanbe_time()
    
    # Рабочее время с 8:00 до 17:00 по Душанбе
    work_start = dushanbe_now.replace(hour=8, minute=0, second=0, microsecond=0)
    work_end = dushanbe_now.replace(hour=17, minute=0, second=0, microsecond=0)
    
    # Если сейчас до начала рабочего дня
    if dushanbe_now < work_start:
        time_left = work_start - dushanbe_now
        hours = time_left.seconds // 3600
        minutes = (time_left.seconds % 3600) // 60
        
        messages = [
            "⏳ До начала рабочего дня: {hours:02d}:{minutes:02d}\n🚀 Не опаздывайте!",
            "⏳ До начала рабочего дня: {hours:02d}:{minutes:02d}\n💼 Готовьтесь к продуктивному дню!",
            "⏳ До начала рабочего дня: {hours:02d}:{minutes:02d}\n☕ Выпейте кофе и будьте готовы!",
            "⏳ До начала рабочего дня: {hours:02d}:{minutes:02d}\n🌟 Новый день - новые возможности!",
            "⏳ До начала рабочего дня: {hours:02d}:{minutes:02d}\n📋 Планируйте свои задачи заранее!",
            "⏳ До начала рабочего дня: {hours:02d}:{minutes:02d}\n🌅 Доброе утро! Скоро начинаем!",
            "⏳ До начала рабочего дня: {hours:02d}:{minutes:02d}\n⚡ Зарядитесь энергией для работы!"
        ]
        message = random.choice(messages)
        return message.format(hours=hours, minutes=minutes)
    
    # Если сейчас рабочее время
    elif work_start <= dushanbe_now <= work_end:
        time_left = work_end - dushanbe_now
        hours = time_left.seconds // 3600
        minutes = (time_left.seconds % 3600) // 60
        
        messages = [
            "⏳ До конца рабочего дня: {hours:02d}:{minutes:02d}\n💪 Успейте завершить все задачи!",
            "⏳ До конца рабочего дня: {hours:02d}:{minutes:02d}\n🎯 Сосредоточьтесь на главном!",
            "⏳ До конца рабочего дня: {hours:02d}:{minutes:02d}\n🚀 Продолжаем работать эффективно!",
            "⏳ До конца рабочего дня: {hours:02d}:{minutes:02d}\n📊 Подведите итоги дня!",
            "⏳ До конца рабочего дня: {hours:02d}:{minutes:02d}\n🌟 Еще есть время для великих дел!",
            "⏳ До конца рабочего дня: {hours:02d}:{minutes:02d}\n⚡ Не сбавляйте темп!",
            "⏳ До конца рабочего дня: {hours:02d}:{minutes:02d}\n🏆 Завершите день победой!"
        ]
        message = random.choice(messages)
        return message.format(hours=hours, minutes=minutes)
    
    # Если рабочий день уже закончился
    else:
        messages = [
            "🏁 Рабочий день завершен\n🌙 Хорошего вечера и отдыхайте!",
            "🏁 Рабочий день завершен\n⭐ Отличная работа сегодня!",
            "🏁 Рабочий день завершен\n💫 Завтра новый продуктивный день!",
            "🏁 Рабочий день завершен\n🌿 Время для отдыха и восстановления!",
            "🏁 Рабочий день завершен\n🎉 Вы хорошо поработали сегодня!"
        ]
        return random.choice(messages)

def edit_daily_report(group_id, message_id):
    """Редактирует сообщение с обновленным обратным отсчетом"""
    try:
        history_text = get_tajikistan_history()
        weather_text = get_dushanbe_weather()
        
        # Получаем обратный отсчет времени работы по Душанбе
        countdown_text = get_work_time_countdown()
        
        message = f"📅 ЕЖЕДНЕВНАЯ СВОДКА\n\n"
        message += history_text + "\n\n"
        message += weather_text + "\n\n"
        message += f"🕐 Время работы: 8:00 - 17:00\n"
        message += f"{countdown_text}\n\n"
        message += "🇹🇯 Государственное унитарное предприятие «Умный город»"
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"
        data = {
            "chat_id": group_id,
            "message_id": message_id,
            "text": message
        }
        
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            print(f"✅ Сообщение обновлено в группе {group_id}! Время Душанбе: {get_dushanbe_time().strftime('%H:%M:%S')}")
            return True
        else:
            print(f"❌ Ошибка обновления в группе {group_id}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка обновления отчета: {e}")
        return False

def send_daily_report(group_id):
    """Отправляет новое сообщение и возвращает его ID"""
    try:
        history_text = get_tajikistan_history()
        weather_text = get_dushanbe_weather()
        
        # Получаем обратный отсчет времени работы по Душанбе
        countdown_text = get_work_time_countdown()
        
        message = f"📅 ЕЖЕДНЕВНАЯ СВОДКА\n\n"
        message += history_text + "\n\n"
        message += weather_text + "\n\n"
        message += f"🕐 Время работы: 8:00 - 17:00\n"
        message += f"{countdown_text}\n\n"
        message += "🇹🇯 Государственное унитарное предприятие «Умный город»"
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": group_id, "text": message}
        
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            message_id = response.json()['result']['message_id']
            print(f"✅ Сообщение отправлено в группу {group_id}! ID: {message_id}")
            return message_id
        else:
            print(f"❌ Ошибка отправки в группу {group_id}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Ошибка формирования отчета: {e}")
        return None

def start_countdown_updates():
    """Запускает обновление обратного отсчета каждую минуту"""
    config = load_config()
    groups = config.get("GROUP_IDS", [])
    
    for group_id in groups:
        if group_id in last_message_ids:
            edit_daily_report(group_id, last_message_ids[group_id])

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
            message_id = send_daily_report(group_id)
            if message_id:
                last_message_ids[group_id] = message_id
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
            message_id = send_daily_report(group_id)
            if message_id:
                last_message_ids[group_id] = message_id
                success_count += 1
        time.sleep(1)
    
    print(f"\n📊 Итог теста: успешно в {success_count}/{len(groups)} групп")

def check_current_time():
    """Проверка текущего времени"""
    current_time = datetime.now()
    dushanbe_time = get_dushanbe_time()
    config = load_config()
    dushanbe_hour = config["SEND_HOUR"]
    dushanbe_minute = config["SEND_MINUTE"]
    
    print(f"\n🕐 ТЕКУЩЕЕ ВРЕМЯ:")
    print(f"   Сервер (UTC): {current_time.hour:02d}:{current_time.minute:02d}:{current_time.second:02d}")
    print(f"   Душанбе (UTC+5): {dushanbe_time.hour:02d}:{dushanbe_time.minute:02d}:{dushanbe_time.second:02d}")
    print(f"   Отправка запланирована на:")
    print(f"   - Душанбе: {dushanbe_hour:02d}:{dushanbe_minute:02d}")

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
    print(f"🔄 ОБНОВЛЕНИЕ ОТСЧЕТА: каждую минуту с 8:00 до 17:00")
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
                message_id = send_daily_report(group_id)
                if message_id:
                    last_message_ids[group_id] = message_id
                    success_count += 1
            time.sleep(1)
        print(f"\n✅ Тест завершен! Успешно: {success_count}/{len(groups)} групп")
    
    print(f"\n{'='*50}")
    print("⏳ Ожидание времени для автоматической отправки...")
    print("🔄 Обратный отсчет будет обновляться каждую минуту")
    print("🎯 Случайные мотивационные сообщения")
    print("="*50)
    
    last_minute = -1
    last_update_minute = -1
    
    while True:
        try:
            current_time = datetime.now()
            dushanbe_time = get_dushanbe_time()
            
            # Проверяем сообщения админа каждую секунду
            check_admin_messages()
            
            # Обновляем обратный отсчет каждую минуту в рабочее время
            if (dushanbe_time.hour >= 8 and dushanbe_time.hour < 17 and 
                current_time.minute != last_update_minute):
                last_update_minute = current_time.minute
                print(f"🔄 Обновление обратного отсчета... Душанбе: {dushanbe_time.strftime('%H:%M')}")
                start_countdown_updates()
            
            # Логируем смену минуты
            if current_time.minute != last_minute:
                last_minute = current_time.minute
                print(f"🕐 Текущее время: Душанбе {dushanbe_time.hour:02d}:{dushanbe_time.minute:02d} | Ожидаем: {dushanbe_hour:02d}:{dushanbe_minute:02d}")
            
            # Проверяем, нужно ли отправить ежедневный отчет
            if should_send_now():
                print(f"\n🎯 ВРЕМЯ ОТПРАВКИ НАСТУПИЛО! Душанбе: {dushanbe_time.strftime('%H:%M:%S')}")
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
