import requests
import json
from history_events import add_event, load_events

TELEGRAM_BOT_TOKEN = "8249137825:AAHChjPuHOdL7Y5su0gYpQnwtDZ4ubfXsl0"

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)

def process_admin_command(message_text, chat_id):
    config = load_config()
    
    # Проверяем админские права
    if chat_id not in config["ADMIN_IDS"]:
        send_telegram_message(chat_id, "❌ Доступ запрещен!")
        return
    
    # Обрабатываем команды
    if message_text.startswith('/start'):
        send_telegram_message(chat_id,
            "👑 Админ-панель Умный Город\n\n"
            "Команды:\n"
            "⏰ /time - Текущие настройки времени\n"  
            "🕐 /settime 14 30 - Установить время (по Душанбе)\n"
            "📅 /addevent 15.11 Событие - Добавить историческое событие\n"
            "📚 /events - Список всех дат с событиями\n"
            "📨 /test - Тестовая отправка в канал\n"
            "⚡ /enable - Включить бота\n"
            "🚫 /disable - Выключить бота\n"
            "🔧 /settings - Показать все настройки"
        )
    
    elif message_text.startswith('/time'):
        send_telegram_message(chat_id,
            f"⏰ Текущие настройки времени:\n"
            f"Время отправки: {config['SEND_HOUR']:02d}:{config['SEND_MINUTE']:02d} (Душанбе)\n"
            f"Статус бота: {'✅ ВКЛЮЧЕН' if config['BOT_ENABLED'] else '❌ ВЫКЛЮЧЕН'}"
        )
    
    elif message_text.startswith('/settime'):
        parts = message_text.split()
        if len(parts) == 3:
            try:
                hour = int(parts[1])
                minute = int(parts[2])
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    config["SEND_HOUR"] = hour
                    config["SEND_MINUTE"] = minute
                    save_config(config)
                    send_telegram_message(chat_id, 
                        f"✅ Время установлено на {hour:02d}:{minute:02d} по Душанбе\n\n"
                        f"📝 Сервер будет запускать отправку в:\n"
                        f"UTC: {(hour - 5)%24:02d}:{minute:02d}\n"
                        f"Душанбе: {hour:02d}:{minute:02d}"
                    )
                else:
                    send_telegram_message(chat_id, "❌ Неверное время! Часы: 0-23, Минуты: 0-59\nПример: /settime 14 30")
            except:
                send_telegram_message(chat_id, "❌ Ошибка! Используйте числа\nПример: /settime 14 30")
        else:
            send_telegram_message(chat_id, "❌ Неверный формат! Пример: /settime 14 30")
    
    elif message_text.startswith('/addevent'):
        parts = message_text.split()
        if len(parts) >= 3:
            try:
                date_str = parts[1]
                event_text = ' '.join(parts[2:])
                day, month = map(int, date_str.split('.'))
                
                # Проверяем валидность даты
                if 1 <= month <= 12 and 1 <= day <= 31:
                    result = add_event(month, day, event_text)
                    send_telegram_message(chat_id, result)
                else:
                    send_telegram_message(chat_id, "❌ Неверная дата! Месяц: 1-12, День: 1-31")
            except:
                send_telegram_message(chat_id, "❌ Ошибка! Пример: /addevent 15.11 1990 – Событие")
        else:
            send_telegram_message(chat_id, "❌ Неверный формат! Пример: /addevent 15.11 1990 – Событие")
    
    elif message_text.startswith('/events'):
        events_db = load_events()
        if not events_db:
            send_telegram_message(chat_id, "📭 В базе нет событий")
            return
        
        message = "📚 Даты с событиями:\n\n"
        for date_key in sorted(events_db.keys()):
            month = int(date_key[:2])
            day = int(date_key[2:])
            count = len(events_db[date_key])
            message += f"📅 {day:02d}.{month:02d} - {count} событий\n"
        
        send_telegram_message(chat_id, message)
    
    elif message_text.startswith('/test'):
        from history_events import get_tajikistan_history
        from weather_service import get_dushanbe_weather
        
        send_telegram_message(chat_id, "🔄 Отправляю тестовое сообщение в канал...")
        
        # Отправляем стикер
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendSticker"
        data = {"chat_id": "-1003104338746", "sticker": "CAACAgIAAxkBAAEPnw5o-adhPImHgSmQpfa-yO9kVk1RxAACwwwAAsVEyEtvpOuf2LbHBDYE"}
        sticker_response = requests.post(url, data=data)
        
        # Отправляем сообщение
        history_text = get_tajikistan_history()
        weather_text = get_dushanbe_weather()
        
        message = "🔄 ТЕСТОВАЯ ОТПРАВКА\n\n"
        message += history_text + "\n"
        message += weather_text + "\n\n"
        message += "📖 Государственное унитарное предприятие «Умный город»"
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": "-1003104338746", "text": message}
        message_response = requests.post(url, data=data)
        
        if message_response.status_code == 200:
            send_telegram_message(chat_id, "✅ Тестовое сообщение отправлено!")
        else:
            send_telegram_message(chat_id, "❌ Ошибка отправки")
    
    elif message_text.startswith('/enable'):
        config["BOT_ENABLED"] = True
        save_config(config)
        send_telegram_message(chat_id, "✅ Бот включен!")
    
    elif message_text.startswith('/disable'):
        config["BOT_ENABLED"] = False
        save_config(config)
        send_telegram_message(chat_id, "✅ Бот выключен!")
    
    elif message_text.startswith('/settings'):
        send_telegram_message(chat_id,
            f"⚙️ Настройки бота:\n\n"
            f"⏰ Время отправки: {config['SEND_HOUR']:02d}:{config['SEND_MINUTE']:02d} (Душанбе)\n"
            f"🔧 Статус: {'✅ ВКЛЮЧЕН' if config['BOT_ENABLED'] else '❌ ВЫКЛЮЧЕН'}\n"
            f"👑 Админов: {len(config['ADMIN_IDS'])}\n"
            f"🆔 Ваш ID: {chat_id}"
        )
    
    else:
        send_telegram_message(chat_id, "❌ Неизвестная команда. Используйте /start для списка команд")

def check_admin_messages():
    """Проверяет новые сообщения от админов"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data["ok"] and data["result"]:
                for update in data["result"]:
                    if "message" in update and "text" in update["message"]:
                        message_text = update["message"]["text"]
                        chat_id = update["message"]["chat"]["id"]
                        process_admin_command(message_text, chat_id)
                
                # Помечаем сообщения как прочитанные
                if data["result"]:
                    last_id = data["result"][-1]["update_id"]
                    requests.get(f"{url}?offset={last_id + 1}")
        return True
    except Exception as e:
        print(f"❌ Ошибка проверки сообщений: {e}")
        return False