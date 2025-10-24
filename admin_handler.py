import requests
import json
import re
from datetime import datetime
from history_events import add_event, load_events, delete_event

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
            ["⏰ Изменить время отправки", "📅 Управление событиями"],
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
            ["🔙 Назад в меню"]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

def get_events_keyboard():
    """Клавиатура для управления событиями"""
    return {
        "keyboard": [
            ["📝 Добавить событие", "📋 Список событий"],
            ["✏️ Изменить событие", "🗑️ Удалить событие"],
            ["🔙 Назад в меню"]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

def get_months_keyboard():
    """Клавиатура для выбора месяца"""
    return {
        "keyboard": [
            ["1️⃣ Январь", "2️⃣ Февраль", "3️⃣ Март"],
            ["4️⃣ Апрель", "5️⃣ Май", "6️⃣ Июнь"],
            ["7️⃣ Июль", "8️⃣ Август", "9️⃣ Сентябрь"],
            ["🔟 Октябрь", "1️⃣1️⃣ Ноябрь", "1️⃣2️⃣ Декабрь"],
            ["🔙 Назад к событиям"]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

def get_days_keyboard(month):
    """Клавиатура для выбора дня месяца"""
    days_in_month = {
        1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30,
        7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
    }
    
    days = []
    row = []
    for day in range(1, days_in_month[month] + 1):
        row.append(f"{day:02d}")
        if len(row) == 5:  # 5 дней в строке
            days.append(row)
            row = []
    if row:
        days.append(row)
    
    days.append(["🔙 Назад к месяцам"])
    
    return {
        "keyboard": days,
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

def get_edit_events_keyboard():
    """Клавиатура для редактирования событий"""
    events_db = load_events()
    keyboard = []
    row = []
    
    for date_key in sorted(events_db.keys())[:20]:  # Ограничиваем 20 датами
        month = int(date_key[:2])
        day = int(date_key[2:])
        button_text = f"📅 {day:02d}.{month:02d}"
        row.append(button_text)
        
        if len(row) == 2:  # 2 даты в строке
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append(["🔙 Назад к событиям"])
    
    return {
        "keyboard": keyboard,
        "resize_keyboard": True,
        "one_time_keyboard": False
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
    
    elif message_text == "📅 управление событиями" or message_text == "📅 Управление событиями":
        send_telegram_message(chat_id,
            "📅 <b>Управление событиями:</b>\n\n"
            "Выберите действие:",
            reply_markup=get_events_keyboard()
        )
        return
    
    elif message_text == "📝 добавить событие" or message_text == "📝 Добавить событие":
        user_states[chat_id] = "selecting_month_for_add"
        send_telegram_message(chat_id,
            "📅 <b>Выберите месяц:</b>",
            reply_markup=get_months_keyboard()
        )
        return
    
    elif message_text == "📋 список событий" or message_text == "📋 Список событий":
        show_events_list(chat_id)
        return
    
    elif message_text == "✏️ изменить событие" or message_text == "✏️ Изменить событие":
        user_states[chat_id] = "selecting_date_for_edit"
        send_telegram_message(chat_id,
            "📅 <b>Выберите дату для редактирования:</b>",
            reply_markup=get_edit_events_keyboard()
        )
        return
    
    elif message_text == "🗑️ удалить событие" or message_text == "🗑️ Удалить событие":
        user_states[chat_id] = "selecting_date_for_delete"
        send_telegram_message(chat_id,
            "🗑️ <b>Выберите дату для удаления событий:</b>",
            reply_markup=get_edit_events_keyboard()
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
    
    elif message_text == "🔙 назад в меню" or message_text == "🔙 Назад в меню":
        user_states.pop(chat_id, None)
        send_telegram_message(chat_id, 
            "👑 <b>Админ-панель Умный Город</b>", 
            reply_markup=get_main_keyboard()
        )
        return
    
    elif message_text == "🔙 назад к событиям" or message_text == "🔙 Назад к событиям":
        user_states.pop(chat_id, None)
        send_telegram_message(chat_id,
            "📅 <b>Управление событиями:</b>",
            reply_markup=get_events_keyboard()
        )
        return
    
    elif message_text == "🔙 назад к месяцам" or message_text == "🔙 Назад к месяцам":
        user_states[chat_id] = "selecting_month_for_add"
        send_telegram_message(chat_id,
            "📅 <b>Выберите месяц:</b>",
            reply_markup=get_months_keyboard()
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
    
    # Обрабатываем выбор месяца
    elif message_text in ["1️⃣ Январь", "2️⃣ Февраль", "3️⃣ Март", "4️⃣ Апрель", "5️⃣ Май", "6️⃣ Июнь",
                         "7️⃣ Июль", "8️⃣ Август", "9️⃣ Сентябрь", "🔟 Октябрь", "1️⃣1️⃣ Ноябрь", "1️⃣2️⃣ Декабрь"]:
        month_map = {
            "1️⃣ Январь": 1, "2️⃣ Февраль": 2, "3️⃣ Март": 3, "4️⃣ Апрель": 4,
            "5️⃣ Май": 5, "6️⃣ Июнь": 6, "7️⃣ Июль": 7, "8️⃣ Август": 8,
            "9️⃣ Сентябрь": 9, "🔟 Октябрь": 10, "1️⃣1️⃣ Ноябрь": 11, "1️⃣2️⃣ Декабрь": 12
        }
        
        month = month_map[message_text]
        current_state = user_states.get(chat_id)
        
        if current_state == "selecting_month_for_add":
            user_states[chat_id] = f"selecting_day_for_add_{month}"
            send_telegram_message(chat_id,
                f"📅 <b>Выберите день месяца:</b>\n\nМесяц: {month:02d}",
                reply_markup=get_days_keyboard(month)
            )
        return
    
    # Обрабатываем выбор дня
    elif re.match(r'^\d{1,2}$', message_text.strip()):
        day = int(message_text.strip())
        current_state = user_states.get(chat_id)
        
        if current_state and current_state.startswith("selecting_day_for_add_"):
            month = int(current_state.split('_')[-1])
            if 1 <= day <= 31:
                user_states[chat_id] = f"waiting_event_text_{month:02d}{day:02d}"
                send_telegram_message(chat_id,
                    f"📝 <b>Введите текст события:</b>\n\n"
                    f"📅 Дата: {day:02d}.{month:02d}\n\n"
                    f"Пример:\n<code>1990 – День независимости Таджикистана</code>",
                    reply_markup=get_cancel_keyboard()
                )
        return
    
    # Обрабатываем выбор даты для редактирования/удаления
    elif message_text.startswith("📅 ") and len(message_text) == 6:
        try:
            date_str = message_text.replace("📅 ", "").strip()
            day, month = map(int, date_str.split('.'))
            current_state = user_states.get(chat_id)
            
            if current_state == "selecting_date_for_edit":
                show_events_for_date(chat_id, month, day, "edit")
            elif current_state == "selecting_date_for_delete":
                show_events_for_date(chat_id, month, day, "delete")
        except:
            pass
        return
    
    # Обрабатываем состояние пользователя
    current_state = user_states.get(chat_id)
    
    if current_state == "waiting_for_time":
        process_time_input(message_text, chat_id, config)
    
    elif current_state == "waiting_for_custom_time":
        process_custom_time_input(message_text, chat_id, config)
    
    elif current_state and current_state.startswith("waiting_event_text_"):
        process_event_input(message_text, chat_id, current_state)
    
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

def process_event_input(message_text, chat_id, current_state):
    """Обрабатывает ввод события"""
    try:
        date_key = current_state.replace("waiting_event_text_", "")
        month = int(date_key[:2])
        day = int(date_key[2:])
        
        if message_text.strip():
            result = add_event(month, day, message_text.strip())
            user_states.pop(chat_id, None)
            send_telegram_message(chat_id, result, reply_markup=get_main_keyboard())
        else:
            send_telegram_message(chat_id, 
                "❌ Текст события не может быть пустым!\n\nПопробуйте снова:",
                reply_markup=get_cancel_keyboard()
            )
    except Exception as e:
        send_telegram_message(chat_id, 
            f"❌ Ошибка: {e}\n\nПопробуйте снова:",
            reply_markup=get_cancel_keyboard()
        )

def show_events_for_date(chat_id, month, day, action_type):
    """Показывает события для выбранной даты"""
    events_db = load_events()
    date_key = f"{month:02d}{day:02d}"
    
    if date_key not in events_db or not events_db[date_key]:
        send_telegram_message(chat_id, 
            f"📭 На дату {day:02d}.{month:02d} нет событий",
            reply_markup=get_edit_events_keyboard()
        )
        return
    
    events = events_db[date_key]
    message = f"📅 <b>События на {day:02d}.{month:02d}:</b>\n\n"
    
    keyboard = []
    for i, event in enumerate(events, 1):
        message += f"{i}. {event}\n"
        if action_type == "delete":
            keyboard.append([f"🗑️ Удалить событие {i}"])
    
    if action_type == "edit":
        message += "\nℹ️ Для редактирования используйте команду:\n"
        message += f"<code>/editevent {day:02d}.{month:02d} НОМЕР Новый текст</code>"
    elif action_type == "delete":
        user_states[chat_id] = f"confirm_delete_{date_key}"
        keyboard.append(["🔙 Назад к датам"])
    
    reply_markup = {"keyboard": keyboard, "resize_keyboard": True} if keyboard else None
    send_telegram_message(chat_id, message, reply_markup=reply_markup)

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

# ... остальные функции остаются без изменений (show_settings, send_test_message, enable_bot, disable_bot и т.д.)
# Просто скопируйте их из предыдущей версии

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
