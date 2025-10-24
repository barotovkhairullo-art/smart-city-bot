import requests
import json
import re
from history_events import add_event, load_events

TELEGRAM_BOT_TOKEN = "8249137825:AAHChjPuHOdL7Y5su0gYpQnwtDZ4ubfXsl0"

# Хранилище состояний пользователей
user_states = {}

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)

def send_telegram_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id, 
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    requests.post(url, data=data)

def get_main_keyboard():
    """Клавиатура главного меню"""
    return {
        "keyboard": [
            ["⏰ Изменить время отправки", "📅 Добавить событие"],
            ["🔧 Настройки бота", "📨 Тестовая отправка"],
            ["✅ Включить бота", "❌ Выключить бота"]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

def get_time_keyboard():
    """Клавиатура для выбора времени"""
    return {
        "keyboard": [
            ["🕐 08:00", "🕐 10:00", "🕐 12:00"],
            ["🕐 14:00", "🕐 16:00", "🕐 18:00"],
            ["🕐 20:00", "🕐 22:00", "✏️ Другое время"],
            ["🔙 Назад"]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

def get_cancel_keyboard():
    """Клавиатура для отмены действия"""
    return {
        "keyboard": [["🔙 Отменить"]],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }

def process_admin_command(message_text, chat_id):
    config = load_config()
    
    # Проверяем админские права
    if chat_id not in config["ADMIN_IDS"]:
        send_telegram_message(chat_id, "❌ Доступ запрещен!")
        return
    
    # Обрабатываем текстовые команды (кнопки)
    if message_text == "⏰ изменить время отправки" or message_text == "⏰ Изменить время отправки":
        user_states[chat_id] = "waiting_for_time"
        send_telegram_message(chat_id,
            "🕐 <b>Выберите время отправки:</b>\n\n"
            "• Нажмите на готовое время\n"
            "• Или введите вручную в формате <code>ЧЧ:ММ</code>\n"
            "• Например: <code>15:30</code>",
            reply_markup=get_time_keyboard()
        )
        return
    
    elif message_text == "📅 добавить событие" or message_text == "📅 Добавить событие":
        user_states[chat_id] = "waiting_for_event"
        send_telegram_message(chat_id,
            "📅 <b>Добавление события:</b>\n\n"
            "Введите событие в формате:\n"
            "<code>ДД.ММ Текст события</code>\n\n"
            "Пример:\n"
            "<code>25.10 1990 – День независимости</code>",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    elif message_text == "🔧 настройки бота" or message_text == "🔧 Настройки бота":
        show_settings(chat_id, config)
        return
    
    elif message_text == "📨 тестовая отправка" or message_text == "📨 Тестовая отправка":
        send_test_message(chat_id)
        return
    
    elif message_text == "✅ включить бота" or message_text == "✅ Включить бота":
        enable_bot(chat_id, config)
        return
    
    elif message_text == "❌ выключить бота" or message_text == "❌ Выключить бота":
        disable_bot(chat_id, config)
        return
    
    elif message_text == "🔙 назад" or message_text == "🔙 Назад":
        user_states.pop(chat_id, None)
        send_telegram_message(chat_id, 
            "👑 <b>Админ-панель Умный Город</b>", 
            reply_markup=get_main_keyboard()
        )
        return
    
    elif message_text == "✏️ другое время" or message_text == "✏️ Другое время":
        user_states[chat_id] = "waiting_for_custom_time"
        send_telegram_message(chat_id,
            "✏️ <b>Введите время вручную:</b>\n\n"
            "Формат: <code>ЧЧ:ММ</code>\n"
            "Пример: <code>15:30</code>\n\n"
            "Время указывается для Душанбе (UTC+5)",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    elif message_text == "🔙 отменить" or message_text == "🔙 Отменить":
        user_states.pop(chat_id, None)
        send_telegram_message(chat_id, 
            "❌ Действие отменено", 
            reply_markup=get_main_keyboard()
        )
        return
    
    # Обрабатываем состояние пользователя
    current_state = user_states.get(chat_id)
    
    if current_state == "waiting_for_time":
        process_time_input(message_text, chat_id, config)
    
    elif current_state == "waiting_for_custom_time":
        process_custom_time_input(message_text, chat_id, config)
    
    elif current_state == "waiting_for_event":
        process_event_input(message_text, chat_id)
    
    # Обрабатываем текстовые команды (старый формат)
    elif message_text.startswith('/'):
        process_text_commands(message_text, chat_id, config)
    
    else:
        # Если неизвестная команда - показываем главное меню
        send_telegram_message(chat_id, 
            "👑 <b>Админ-панель Умный Город</b>\n\n"
            "Используйте кнопки ниже для управления:",
            reply_markup=get_main_keyboard()
        )

def process_time_input(message_text, chat_id, config):
    """Обрабатывает ввод времени из кнопок"""
    time_match = re.match(r'🕐\s*(\d{1,2}):(\d{2})', message_text)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2))
        set_time_config(chat_id, config, hour, minute)
    else:
        send_telegram_message(chat_id, 
            "❌ Неверный формат времени. Используйте кнопки или введите в формате ЧЧ:ММ",
            reply_markup=get_time_keyboard()
        )

def process_custom_time_input(message_text, chat_id, config):
    """Обрабатывает ручной ввод времени"""
    time_match = re.match(r'(\d{1,2}):(\d{2})', message_text)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2))
        set_time_config(chat_id, config, hour, minute)
    else:
        send_telegram_message(chat_id, 
            "❌ Неверный формат времени!\n\n"
            "Введите время в формате: <code>ЧЧ:ММ</code>\n"
            "Пример: <code>15:30</code>",
            reply_markup=get_cancel_keyboard()
        )

def process_event_input(message_text, chat_id):
    """Обрабатывает ввод события"""
    parts = message_text.split()
    if len(parts) >= 2:
        try:
            date_str = parts[0]
            event_text = ' '.join(parts[1:])
            
            if '.' in date_str:
                day, month = map(int, date_str.split('.'))
                
                # Проверяем валидность даты
                if 1 <= month <= 12 and 1 <= day <= 31:
                    result = add_event(month, day, event_text)
                    user_states.pop(chat_id, None)
                    send_telegram_message(chat_id, result, reply_markup=get_main_keyboard())
                else:
                    send_telegram_message(chat_id, 
                        "❌ Неверная дата!\nМесяц: 1-12, День: 1-31\n\nПопробуйте снова:",
                        reply_markup=get_cancel_keyboard()
                    )
            else:
                send_telegram_message(chat_id, 
                    "❌ Неверный формат даты!\nИспользуйте: ДД.ММ\n\nПопробуйте снова:",
                    reply_markup=get_cancel_keyboard()
                )
        except Exception as e:
            send_telegram_message(chat_id, 
                f"❌ Ошибка: {e}\n\nПопробуйте снова:",
                reply_markup=get_cancel_keyboard()
            )
    else:
        send_telegram_message(chat_id, 
            "❌ Неверный формат!\nВведите: ДД.ММ Текст события\n\nПопробуйте снова:",
            reply_markup=get_cancel_keyboard()
        )

def set_time_config(chat_id, config, hour, minute):
    """Устанавливает время в конфиг"""
    if 0 <= hour <= 23 and 0 <= minute <= 59:
        config["SEND_HOUR"] = hour
        config["SEND_MINUTE"] = minute
        save_config(config)
        user_states.pop(chat_id, None)
        
        # Конвертируем в UTC для сервера
        utc_hour = (hour - 5) % 24
        
        send_telegram_message(chat_id,
            f"✅ <b>Время установлено!</b>\n\n"
            f"🕐 <b>Душанбе:</b> {hour:02d}:{minute:02d} (UTC+5)\n"
            f"🌐 <b>Сервер:</b> {utc_hour:02d}:{minute:02d} (UTC)\n\n"
            f"Следующая отправка будет в {hour:02d}:{minute:02d} по Душанбе",
            reply_markup=get_main_keyboard()
        )
    else:
        send_telegram_message(chat_id, 
            "❌ Неверное время!\nЧасы: 0-23, Минуты: 0-59",
            reply_markup=get_time_keyboard()
        )

def process_text_commands(message_text, chat_id, config):
    """Обрабатывает текстовые команды (старый формат)"""
    if message_text.startswith('/start'):
        send_telegram_message(chat_id, 
            "👑 <b>Админ-панель Умный Город</b>\n\n"
            "Используйте кнопки ниже для управления:",
            reply_markup=get_main_keyboard()
        )
    
    elif message_text.startswith('/settime'):
        parts = message_text.split()
        if len(parts) == 3:
            try:
                hour = int(parts[1])
                minute = int(parts[2])
                set_time_config(chat_id, config, hour, minute)
            except:
                send_telegram_message(chat_id, "❌ Ошибка! Пример: /settime 14 30")
        else:
            send_telegram_message(chat_id, "❌ Неверный формат! Пример: /settime 14 30")
    
    elif message_text.startswith('/time'):
        show_time_settings(chat_id, config)
    
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
    
    elif message_text.startswith('/events'):
        show_events_list(chat_id)
    
    elif message_text.startswith('/test'):
        send_test_message(chat_id)
    
    elif message_text.startswith('/enable'):
        enable_bot(chat_id, config)
    
    elif message_text.startswith('/disable'):
        disable_bot(chat_id, config)
    
    elif message_text.startswith('/settings'):
        show_settings(chat_id, config)
    
    else:
        send_telegram_message(chat_id, 
            "❌ Неизвестная команда",
            reply_markup=get_main_keyboard()
        )

def show_time_settings(chat_id, config):
    """Показывает настройки времени"""
    utc_hour = (config["SEND_HOUR"] - 5) % 24
    send_telegram_message(chat_id,
        f"⏰ <b>Текущие настройки времени:</b>\n\n"
        f"🕐 <b>Душанбе:</b> {config['SEND_HOUR']:02d}:{config['SEND_MINUTE']:02d} (UTC+5)\n"
        f"🌐 <b>Сервер:</b> {utc_hour:02d}:{config['SEND_MINUTE']:02d} (UTC)\n"
        f"🔧 <b>Статус:</b> {'✅ ВКЛЮЧЕН' if config['BOT_ENABLED'] else '❌ ВЫКЛЮЧЕН'}"
    )

def show_settings(chat_id, config):
    """Показывает все настройки"""
    utc_hour = (config["SEND_HOUR"] - 5) % 24
    send_telegram_message(chat_id,
        f"⚙️ <b>Настройки бота:</b>\n\n"
        f"🕐 <b>Время отправки:</b>\n"
        f"   📍 Душанбе: {config['SEND_HOUR']:02d}:{config['SEND_MINUTE']:02d} (UTC+5)\n"
        f"   🌐 Сервер: {utc_hour:02d}:{config['SEND_MINUTE']:02d} (UTC)\n\n"
        f"🔧 <b>Статус бота:</b> {'✅ ВКЛЮЧЕН' if config['BOT_ENABLED'] else '❌ ВЫКЛЮЧЕН'}\n"
        f"👑 <b>Админов:</b> {len(config['ADMIN_IDS'])}\n"
        f"🆔 <b>Ваш ID:</b> {chat_id}"
    )

def show_events_list(chat_id):
    """Показывает список событий"""
    events_db = load_events()
    if not events_db:
        send_telegram_message(chat_id, "📭 В базе нет событий")
        return
    
    message = "📚 <b>Даты с событиями:</b>\n\n"
    for date_key in sorted(events_db.keys()):
        month = int(date_key[:2])
        day = int(date_key[2:])
        count = len(events_db[date_key])
        message += f"📅 {day:02d}.{month:02d} - {count} событий\n"
    
    send_telegram_message(chat_id, message)

def send_test_message(chat_id):
    """Отправляет тестовое сообщение"""
    from history_events import get_tajikistan_history
    from weather_service import get_dushanbe_weather
    
    send_telegram_message(chat_id, "🔄 Отправляю тестовое сообщение в канал...")
    
    try:
        # Отправляем стикер
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendSticker"
        data = {"chat_id": "-1003104338746", "sticker": "CAACAgIAAxkBAAEPnw5o-adhPImHgSmQpfa-yO9kVk1RxAACwwwAAsVEyEtvpOuf2LbHBDYE"}
        requests.post(url, data=data)
        
        # Отправляем сообщение
        history_text = get_tajikistan_history()
        weather_text = get_dushanbe_weather()
        
        message = "🔄 ТЕСТОВАЯ ОТПРАВКА\n\n"
        message += history_text + "\n"
        message += weather_text + "\n\n"
        message += "📖 Государственное унитарное предприятие «Умный город»"
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {"chat_id": "-1003104338746", "text": message}
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            send_telegram_message(chat_id, "✅ Тестовое сообщение отправлено!")
        else:
            send_telegram_message(chat_id, "❌ Ошибка отправки")
    except Exception as e:
        send_telegram_message(chat_id, f"❌ Ошибка: {e}")

def enable_bot(chat_id, config):
    """Включает бота"""
    config["BOT_ENABLED"] = True
    save_config(config)
    send_telegram_message(chat_id, "✅ Бот включен!")

def disable_bot(chat_id, config):
    """Выключает бота"""
    config["BOT_ENABLED"] = False
    save_config(config)
    send_telegram_message(chat_id, "✅ Бот выключен!")

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
