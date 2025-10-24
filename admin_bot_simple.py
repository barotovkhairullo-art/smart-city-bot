import requests
import json
from history_events import add_event, load_events
from weather_service import get_dushanbe_weather

TELEGRAM_BOT_TOKEN = "8249137825:AAHChjPuHOdL7Y5su0gYpQnwtDZ4ubfXsl0"
CHANNEL_ID = "-1003104338746"
STICKER_ID = "CAACAgIAAxkBAAEPnw5o-adhPImHgSmQpfa-yO9kVk1RxAACwwwAAsVEyEtvpOuf2LbHBDYE"

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
            "⏰ /time - Настройки времени\n"  
            "🕐 /settime 14 30 - Установить время\n"
            "📅 /addevent 15.11 Событие\n"
            "📨 /test - Тестовая отправка\n"
            "⚡ /enable - Включить бота\n"
            "🚫 /disable - Выключить бота"
        )
    
    elif message_text.startswith('/time'):
        send_telegram_message(chat_id,
            f"⏰ Текущие настройки:\n"
            f"Время: {config['SEND_HOUR']:02d}:{config['SEND_MINUTE']:02d}\n"
            f"Статус: {'✅ ВКЛЮЧЕН' if config['BOT_ENABLED'] else '❌ ВЫКЛЮЧЕН'}"
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
                    send_telegram_message(chat_id, f"✅ Время установлено на {hour:02d}:{minute:02d}")
                else:
                    send_telegram_message(chat_id, "❌ Неверное время! Пример: /settime 14 30")
            except:
                send_telegram_message(chat_id, "❌ Ошибка! Пример: /settime 14 30")
    
    elif message_text.startswith('/addevent'):
        parts = message_text.split()
        if len(parts) >= 3:
            try:
                date_str = parts[1]
                event_text = ' '.join(parts[2:])
                day, month = map(int, date_str.split('.'))
                result = add_event(month, day, event_text)
                send_telegram_message(chat_id, result)
            except:
                send_telegram_message(chat_id, "❌ Ошибка! Пример: /addevent 15.11 1990 – Событие")
    
    elif message_text.startswith('/test'):
        from history_events import get_tajikistan_history
        
        # Отправляем стикер
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendSticker"
        data = {"chat_id": CHANNEL_ID, "sticker": STICKER_ID}
        requests.post(url, data=data)
        
        # Отправляем сообщение
        history_text = get_tajikistan_history()
        weather_text = get_dushanbe_weather()
        
        message = "🔄 ТЕСТОВАЯ ОТПРАВКА\n\n"
        message += history_text + "\n"
        message += weather_text + "\n\n"
        message += "📖 Государственное унитарное предприятие «Умный город»"
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHANNEL_ID, "text": message}
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
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
    
    else:
        send_telegram_message(chat_id, "❌ Неизвестная команда. Используй /start")

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
    except:
        return False