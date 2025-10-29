import requests
import json
import re
from datetime import datetime
from history_events import add_event, load_events, delete_event

TELEGRAM_BOT_TOKEN = "8404371791:AAG-uiZ7Oab4udWZsb5HgijR56dPMPBH9W0"
user_states = {}

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)

def send_telegram_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    requests.post(url, data=data)

def get_main_keyboard():
    return {
        "keyboard": [
            ["⏰ Изменить время сводки", "🕐 Изменить время работы"],
            ["📅 Управление событиями", "👥 Управление группами"],
            ["🔧 Настройки", "📨 Тестовая отправка"],
            ["✅ Вкл/❌ Выкл бота"]
        ],
        "resize_keyboard": True
    }

def get_time_keyboard():
    return {
        "keyboard": [
            ["🕐 07:00", "🕐 08:00", "🕐 09:00"],
            ["🕐 10:00", "🕐 12:00", "🕐 14:00"],
            ["🕐 16:00", "🕐 18:00", "✏️ Другое время"],
            ["🔙 Назад"]
        ],
        "resize_keyboard": True
    }

def get_working_hours_keyboard():
    return {
        "keyboard": [
            ["🕐 06:30", "🕐 07:00", "🕐 07:30"],
            ["🕐 08:00", "🕐 08:30", "🕐 09:00"],
            ["✏️ Другое время", "🔙 Назад"]
        ],
        "resize_keyboard": True
    }

def get_events_keyboard():
    return {
        "keyboard": [
            ["📝 Добавить событие", "📋 Список событий"],
            ["✏️ Изменить событие", "🗑️ Удалить событие"],
            ["🔙 Назад"]
        ],
        "resize_keyboard": True
    }

def get_groups_keyboard():
    return {
        "keyboard": [
            ["➕ Добавить группу", "📋 Список групп"],
            ["✏️ Изменить группу", "🗑️ Удалить группу"],
            ["🔙 Назад"]
        ],
        "resize_keyboard": True
    }

def get_months_keyboard():
    return {
        "keyboard": [
            ["1️⃣ Январь", "2️⃣ Февраль", "3️⃣ Март"],
            ["4️⃣ Апрель", "5️⃣ Май", "6️⃣ Июнь"],
            ["7️⃣ Июль", "8️⃣ Август", "9️⃣ Сентябрь"],
            ["🔟 Октябрь", "1️⃣1️⃣ Ноябрь", "1️⃣2️⃣ Декабрь"],
            ["🔙 Назад"]
        ],
        "resize_keyboard": True
    }

def get_days_keyboard(month):
    days_in_month = {
        1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30,
        7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
    }
    days = []
    row = []
    for day in range(1, days_in_month[month] + 1):
        row.append(f"{day:02d}")
        if len(row) == 5:
            days.append(row)
            row = []
    if row:
        days.append(row)
    days.append(["🔙 Назад"])
    return {"keyboard": days, "resize_keyboard": True}

def get_cancel_keyboard():
    return {"keyboard": [["🔙 Отменить"]], "resize_keyboard": True}

def get_edit_events_keyboard():
    events_db = load_events()
    keyboard = []
    row = []
    for date_key in sorted(events_db.keys())[:20]:
        month = int(date_key[:2])
        day = int(date_key[2:])
        row.append(f"📅 {day:02d}.{month:02d}")
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append(["🔙 Назад"])
    return {"keyboard": keyboard, "resize_keyboard": True}

def get_groups_list_keyboard():
    config = load_config()
    keyboard = []
    row = []
    for i, group_id in enumerate(config.get("GROUP_IDS", [])):
        row.append(f"👥 Группа {i+1}")
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append(["🔙 Назад"])
    return {"keyboard": keyboard, "resize_keyboard": True}

def process_admin_command(message_text, chat_id):
    config = load_config()
    if chat_id not in config["ADMIN_IDS"]:
        send_telegram_message(chat_id, "❌ Доступ запрещен!")
        return

    if message_text in ["⏰ Изменить время сводки", "⏰ изменить время сводки"]:
        user_states[chat_id] = "waiting_for_daily_time"
        send_telegram_message(chat_id, "🕐 Выберите время для ежедневной сводки:", reply_markup=get_time_keyboard())
        return

    elif message_text in ["🕐 Изменить время работы", "🕐 изменить время работы"]:
        user_states[chat_id] = "waiting_for_working_hours_time"
        send_telegram_message(chat_id, "🕐 Выберите время для отправки информации о времени работы:", reply_markup=get_working_hours_keyboard())
        return

    elif message_text in ["📅 Управление событиями", "📅 управление событиями"]:
        send_telegram_message(chat_id, "📅 Управление событиями:", reply_markup=get_events_keyboard())
        return

    elif message_text in ["👥 Управление группами", "👥 управление группами"]:
        send_telegram_message(chat_id, "👥 Управление группами:", reply_markup=get_groups_keyboard())
        return

    elif message_text in ["📝 Добавить событие", "📝 добавить событие"]:
        user_states[chat_id] = "selecting_month_for_add"
        send_telegram_message(chat_id, "📅 Выберите месяц:", reply_markup=get_months_keyboard())
        return

    elif message_text in ["📋 Список событий", "📋 список событий"]:
        show_events_list(chat_id)
        return

    elif message_text in ["✏️ Изменить событие", "✏️ изменить событие"]:
        user_states[chat_id] = "selecting_date_for_edit"
        send_telegram_message(chat_id, "📅 Выберите дату:", reply_markup=get_edit_events_keyboard())
        return

    elif message_text in ["🗑️ Удалить событие", "🗑️ удалить событие"]:
        user_states[chat_id] = "selecting_date_for_delete"
        send_telegram_message(chat_id, "🗑️ Выберите дату:", reply_markup=get_edit_events_keyboard())
        return

    elif message_text in ["➕ Добавить группу", "➕ добавить группу"]:
        user_states[chat_id] = "waiting_for_group_id"
        send_telegram_message(chat_id, "➕ Введите ID группы:\n\nПример: -1001234567890", reply_markup=get_cancel_keyboard())
        return

    elif message_text in ["📋 Список групп", "📋 список групп"]:
        show_groups_list(chat_id)
        return

    elif message_text in ["✏️ Изменить группу", "✏️ изменить группу"]:
        user_states[chat_id] = "selecting_group_to_edit"
        send_telegram_message(chat_id, "✏️ Выберите группу для редактирования:", reply_markup=get_groups_list_keyboard())
        return

    elif message_text in ["🗑️ Удалить группу", "🗑️ удалить группу"]:
        user_states[chat_id] = "selecting_group_to_delete"
        send_telegram_message(chat_id, "🗑️ Выберите группу для удаления:", reply_markup=get_groups_list_keyboard())
        return

    elif message_text in ["🔧 Настройки", "🔧 настройки"]:
        show_settings(chat_id, config)
        return

    elif message_text in ["📨 Тестовая отправка", "📨 тестовая отправка"]:
        send_test_message(chat_id)
        return

    elif message_text in ["✅ Вкл/❌ Выкл бота", "✅ вкл/❌ выкл бота"]:
        toggle_bot(chat_id, config)
        return

    elif message_text in ["🔙 Назад", "🔙 назад", "🔙 Отменить", "🔙 отменить"]:
        user_states.pop(chat_id, None)
        send_telegram_message(chat_id, "👑 Админ-панель", reply_markup=get_main_keyboard())
        return

    elif message_text == "✏️ Другое время":
        current_state = user_states.get(chat_id)
        if current_state == "waiting_for_daily_time":
            user_states[chat_id] = "waiting_for_custom_daily_time"
            send_telegram_message(chat_id, "✏️ Введите время для ежедневной сводки ЧЧ:ММ", reply_markup=get_cancel_keyboard())
        elif current_state == "waiting_for_working_hours_time":
            user_states[chat_id] = "waiting_for_custom_working_hours_time"
            send_telegram_message(chat_id, "✏️ Введите время для отправки информации о времени работы ЧЧ:ММ", reply_markup=get_cancel_keyboard())
        return

    if message_text.startswith("👥 Группа "):
        group_index = int(message_text.replace("👥 Группа ", "")) - 1
        current_state = user_states.get(chat_id)
        
        if current_state == "selecting_group_to_edit":
            user_states[chat_id] = f"waiting_new_group_id_{group_index}"
            config = load_config()
            current_group_id = config.get("GROUP_IDS", [])[group_index]
            send_telegram_message(chat_id, f"✏️ Текущий ID группы: {current_group_id}\nВведите новый ID группы:", reply_markup=get_cancel_keyboard())
        elif current_state == "selecting_group_to_delete":
            delete_group(chat_id, group_index)
        return

    month_map = {
        "1️⃣ Январь": 1, "2️⃣ Февраль": 2, "3️⃣ Март": 3, "4️⃣ Апрель": 4,
        "5️⃣ Май": 5, "6️⃣ Июнь": 6, "7️⃣ Июль": 7, "8️⃣ Август": 8,
        "9️⃣ Сентябрь": 9, "🔟 Октябрь": 10, "1️⃣1️⃣ Ноябрь": 11, "1️⃣2️⃣ Декабрь": 12
    }
    if message_text in month_map:
        month = month_map[message_text]
        current_state = user_states.get(chat_id)
        if current_state == "selecting_month_for_add":
            user_states[chat_id] = f"selecting_day_for_add_{month}"
            send_telegram_message(chat_id, f"📅 Выберите день:", reply_markup=get_days_keyboard(month))
        return

    if re.match(r'^\d{1,2}$', message_text.strip()):
        day = int(message_text.strip())
        current_state = user_states.get(chat_id)
        if current_state and current_state.startswith("selecting_day_for_add_"):
            month = int(current_state.split('_')[-1])
            if 1 <= day <= 31:
                user_states[chat_id] = f"waiting_event_text_{month:02d}{day:02d}"
                send_telegram_message(chat_id, f"📝 Введите текст события для {day:02d}.{month:02d}:", reply_markup=get_cancel_keyboard())
        return

    if message_text.startswith("📅 ") and len(message_text) == 6:
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

    current_state = user_states.get(chat_id)
    
    if current_state == "waiting_for_daily_time":
        process_daily_time_input(message_text, chat_id, config)
    elif current_state == "waiting_for_working_hours_time":
        process_working_hours_time_input(message_text, chat_id, config)
    elif current_state == "waiting_for_custom_daily_time":
        process_custom_daily_time_input(message_text, chat_id, config)
    elif current_state == "waiting_for_custom_working_hours_time":
        process_custom_working_hours_time_input(message_text, chat_id, config)
    elif current_state and current_state.startswith("waiting_event_text_"):
        process_event_input(message_text, chat_id, current_state)
    elif current_state == "waiting_for_group_id":
        add_group(chat_id, message_text)
    elif current_state and current_state.startswith("waiting_new_group_id_"):
        group_index = int(current_state.split('_')[-1])
        edit_group(chat_id, group_index, message_text)
    elif message_text.startswith('/'):
        process_text_commands(message_text, chat_id, config)
    else:
        send_telegram_message(chat_id, "👑 Админ-панель", reply_markup=get_main_keyboard())

def process_daily_time_input(message_text, chat_id, config):
    time_match = re.match(r'🕐\s*(\d{1,2}):(\d{2})', message_text)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2))
        set_daily_time_config(chat_id, config, hour, minute)
    else:
        send_telegram_message(chat_id, "❌ Неверный формат", reply_markup=get_time_keyboard())

def process_working_hours_time_input(message_text, chat_id, config):
    time_match = re.match(r'🕐\s*(\d{1,2}):(\d{2})', message_text)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2))
        set_working_hours_time_config(chat_id, config, hour, minute)
    else:
        send_telegram_message(chat_id, "❌ Неверный формат", reply_markup=get_working_hours_keyboard())

def process_custom_daily_time_input(message_text, chat_id, config):
    time_match = re.match(r'(\d{1,2}):(\d{2})', message_text)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2))
        set_daily_time_config(chat_id, config, hour, minute)
    else:
        send_telegram_message(chat_id, "❌ Неверный формат", reply_markup=get_cancel_keyboard())

def process_custom_working_hours_time_input(message_text, chat_id, config):
    time_match = re.match(r'(\d{1,2}):(\d{2})', message_text)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2))
        set_working_hours_time_config(chat_id, config, hour, minute)
    else:
        send_telegram_message(chat_id, "❌ Неверный формат", reply_markup=get_cancel_keyboard())

def process_event_input(message_text, chat_id, current_state):
    try:
        date_key = current_state.replace("waiting_event_text_", "")
        month = int(date_key[:2])
        day = int(date_key[2:])
        if message_text.strip():
            result = add_event(month, day, message_text.strip())
            user_states.pop(chat_id, None)
            send_telegram_message(chat_id, result, reply_markup=get_main_keyboard())
        else:
            send_telegram_message(chat_id, "❌ Введите текст", reply_markup=get_cancel_keyboard())
    except Exception as e:
        send_telegram_message(chat_id, f"❌ Ошибка: {e}", reply_markup=get_cancel_keyboard())

def show_events_for_date(chat_id, month, day, action_type):
    events_db = load_events()
    date_key = f"{month:02d}{day:02d}"
    if date_key not in events_db or not events_db[date_key]:
        send_telegram_message(chat_id, f"📭 Нет событий на {day:02d}.{month:02d}", reply_markup=get_edit_events_keyboard())
        return
    events = events_db[date_key]
    message = f"📅 События на {day:02d}.{month:02d}:\n\n"
    keyboard = []
    for i, event in enumerate(events, 1):
        message += f"{i}. {event}\n"
        if action_type == "delete":
            keyboard.append([f"🗑️ Удалить событие {i}"])
    if action_type == "edit":
        message += f"\nℹ️ Для редактирования: /editevent {day:02d}.{month:02d} НОМЕР Новый текст"
    elif action_type == "delete":
        user_states[chat_id] = f"confirm_delete_{date_key}"
        keyboard.append(["🔙 Назад"])
    reply_markup = {"keyboard": keyboard, "resize_keyboard": True} if keyboard else None
    send_telegram_message(chat_id, message, reply_markup=reply_markup)

def set_daily_time_config(chat_id, config, hour, minute):
    if 0 <= hour <= 23 and 0 <= minute <= 59:
        config["SEND_HOUR"] = hour
        config["SEND_MINUTE"] = minute
        save_config(config)
        user_states.pop(chat_id, None)
        utc_hour = (hour - 5) % 24
        send_telegram_message(chat_id, f"✅ Время ежедневной сводки установлено!\n🕐 Душанбе: {hour:02d}:{minute:02d}\n🌐 Сервер: {utc_hour:02d}:{minute:02d} UTC", reply_markup=get_main_keyboard())
    else:
        send_telegram_message(chat_id, "❌ Неверное время", reply_markup=get_time_keyboard())

def set_working_hours_time_config(chat_id, config, hour, minute):
    if 0 <= hour <= 23 and 0 <= minute <= 59:
        config["WORKING_HOURS_HOUR"] = hour
        config["WORKING_HOURS_MINUTE"] = minute
        save_config(config)
        user_states.pop(chat_id, None)
        utc_hour = (hour - 5) % 24
        send_telegram_message(chat_id, f"✅ Время отправки информации о работе установлено!\n🕐 Душанбе: {hour:02d}:{minute:02d}\n🌐 Сервер: {utc_hour:02d}:{minute:02d} UTC", reply_markup=get_main_keyboard())
    else:
        send_telegram_message(chat_id, "❌ Неверное время", reply_markup=get_working_hours_keyboard())

def show_events_list(chat_id):
    events_db = load_events()
    if not events_db:
        send_telegram_message(chat_id, "📭 Нет событий")
        return
    message = "📚 Даты с событиями:\n\n"
    for date_key in sorted(events_db.keys()):
        month = int(date_key[:2])
        day = int(date_key[2:])
        count = len(events_db[date_key])
        message += f"📅 {day:02d}.{month:02d} - {count} событий\n"
    send_telegram_message(chat_id, message)

def show_settings(chat_id, config):
    utc_daily_hour = (config["SEND_HOUR"] - 5) % 24
    utc_working_hours_hour = (config["WORKING_HOURS_HOUR"] - 5) % 24
    send_telegram_message(chat_id, f"⚙️ Настройки:\n\n📅 Ежедневная сводка:\n🕐 Душанбе: {config['SEND_HOUR']:02d}:{config['SEND_MINUTE']:02d}\n🌐 Сервер: {utc_daily_hour:02d}:{config['SEND_MINUTE']:02d}\n\n🕐 Время работы:\n🕐 Душанбе: {config['WORKING_HOURS_HOUR']:02d}:{config['WORKING_HOURS_MINUTE']:02d}\n🌐 Сервер: {utc_working_hours_hour:02d}:{config['WORKING_HOURS_MINUTE']:02d}\n\n🔧 Статус: {'✅ ВКЛ' if config['BOT_ENABLED'] else '❌ ВЫКЛ'}\n👑 Админов: {len(config['ADMIN_IDS'])}\n👥 Групп: {len(config.get('GROUP_IDS', []))}\n🆔 Ваш ID: {chat_id}")

def send_test_message(chat_id):
    from history_events import get_tajikistan_history
    from weather_service import get_dushanbe_weather
    send_telegram_message(chat_id, "🔄 Отправляю тест...")
    try:
        config = load_config()
        groups = config.get("GROUP_IDS", [])
        
        for group_id in groups:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendSticker"
            data = {"chat_id": group_id, "sticker": "CAACAgIAAxkBAAEPnw5o-adhPImHgSmQpfa-yO9kVk1RxAACwwwAAsVEyEtvpOuf2LbHBDYE"}
            requests.post(url, data=data)
            
            history_text = get_tajikistan_history()
            weather_text = get_dushanbe_weather()
            message = "🔄 ТЕСТОВАЯ ОТПРАВКА\n\n" + history_text + "\n" + weather_text + "\n\n🇹🇯 Государственное унитарное предприятие «Умный город»"
            
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {"chat_id": group_id, "text": message}
            response = requests.post(url, data=data)
            
        send_telegram_message(chat_id, f"✅ Тест отправлен в {len(groups)} групп!")
    except Exception as e:
        send_telegram_message(chat_id, f"❌ Ошибка: {e}")

def toggle_bot(chat_id, config):
    config["BOT_ENABLED"] = not config["BOT_ENABLED"]
    save_config(config)
    status = "✅ ВКЛЮЧЕН" if config["BOT_ENABLED"] else "❌ ВЫКЛЮЧЕН"
    send_telegram_message(chat_id, f"✅ Бот {status.lower()}!")

def add_group(chat_id, group_id):
    try:
        config = load_config()
        if "GROUP_IDS" not in config:
            config["GROUP_IDS"] = []
        
        if not group_id.startswith('-100'):
            send_telegram_message(chat_id, "❌ ID группы должен начинаться с -100\nПример: -1001234567890", reply_markup=get_cancel_keyboard())
            return
        
        if group_id in config["GROUP_IDS"]:
            send_telegram_message(chat_id, "❌ Группа уже добавлена", reply_markup=get_cancel_keyboard())
            return
        
        config["GROUP_IDS"].append(group_id)
        save_config(config)
        user_states.pop(chat_id, None)
        send_telegram_message(chat_id, f"✅ Группа добавлена!\nID: {group_id}", reply_markup=get_main_keyboard())
    except Exception as e:
        send_telegram_message(chat_id, f"❌ Ошибка: {e}", reply_markup=get_cancel_keyboard())

def edit_group(chat_id, group_index, new_group_id):
    try:
        config = load_config()
        if "GROUP_IDS" not in config or group_index >= len(config["GROUP_IDS"]):
            send_telegram_message(chat_id, "❌ Группа не найдена", reply_markup=get_cancel_keyboard())
            return
        
        if not new_group_id.startswith('-100'):
            send_telegram_message(chat_id, "❌ ID группы должен начинаться с -100", reply_markup=get_cancel_keyboard())
            return
        
        old_group_id = config["GROUP_IDS"][group_index]
        config["GROUP_IDS"][group_index] = new_group_id
        save_config(config)
        user_states.pop(chat_id, None)
        send_telegram_message(chat_id, f"✅ Группа изменена!\nСтарый ID: {old_group_id}\nНовый ID: {new_group_id}", reply_markup=get_main_keyboard())
    except Exception as e:
        send_telegram_message(chat_id, f"❌ Ошибка: {e}", reply_markup=get_cancel_keyboard())

def delete_group(chat_id, group_index):
    try:
        config = load_config()
        if "GROUP_IDS" not in config or group_index >= len(config["GROUP_IDS"]):
            send_telegram_message(chat_id, "❌ Группа не найдена")
            return
        
        deleted_group = config["GROUP_IDS"].pop(group_index)
        save_config(config)
        user_states.pop(chat_id, None)
        send_telegram_message(chat_id, f"✅ Группа удалена!\nID: {deleted_group}", reply_markup=get_main_keyboard())
    except Exception as e:
        send_telegram_message(chat_id, f"❌ Ошибка: {e}")

def show_groups_list(chat_id):
    config = load_config()
    groups = config.get("GROUP_IDS", [])
    
    if not groups:
        send_telegram_message(chat_id, "📭 Нет добавленных групп")
        return
    
    message = "👥 Список групп:\n\n"
    for i, group_id in enumerate(groups, 1):
        message += f"{i}. ID: {group_id}\n"
    
    send_telegram_message(chat_id, message)

def process_text_commands(message_text, chat_id, config):
    if message_text.startswith('/start'):
        send_telegram_message(chat_id, "👑 Админ-панель", reply_markup=get_main_keyboard())
    elif message_text.startswith('/settime'):
        parts = message_text.split()
        if len(parts) == 3:
            try:
                hour = int(parts[1])
                minute = int(parts[2])
                set_daily_time_config(chat_id, config, hour, minute)
            except:
                send_telegram_message(chat_id, "❌ Ошибка! Пример: /settime 14 30")
    elif message_text.startswith('/setworkingtime'):
        parts = message_text.split()
        if len(parts) == 3:
            try:
                hour = int(parts[1])
                minute = int(parts[2])
                set_working_hours_time_config(chat_id, config, hour, minute)
            except:
                send_telegram_message(chat_id, "❌ Ошибка! Пример: /setworkingtime 7 30")
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
        send_telegram_message(chat_id, "❌ Неизвестная команда", reply_markup=get_main_keyboard())

def show_time_settings(chat_id, config):
    utc_daily_hour = (config["SEND_HOUR"] - 5) % 24
    utc_working_hours_hour = (config["WORKING_HOURS_HOUR"] - 5) % 24
    send_telegram_message(chat_id, f"⏰ Время отправки:\n\n📅 Ежедневная сводка:\n🕐 Душанбе: {config['SEND_HOUR']:02d}:{config['SEND_MINUTE']:02d}\n🌐 Сервер: {utc_daily_hour:02d}:{config['SEND_MINUTE']:02d} UTC\n\n🕐 Время работы:\n🕐 Душанбе: {config['WORKING_HOURS_HOUR']:02d}:{config['WORKING_HOURS_MINUTE']:02d}\n🌐 Сервер: {utc_working_hours_hour:02d}:{config['WORKING_HOURS_MINUTE']:02d} UTC\n\n🔧 Статус: {'✅ ВКЛ' if config['BOT_ENABLED'] else '❌ ВЫКЛ'}")

def enable_bot(chat_id, config):
    config["BOT_ENABLED"] = True
    save_config(config)
    send_telegram_message(chat_id, "✅ Бот включен!")

def disable_bot(chat_id, config):
    config["BOT_ENABLED"] = False
    save_config(config)
    send_telegram_message(chat_id, "✅ Бот выключен!")

def check_admin_messages():
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
                        
                        # Проверяем, что это личное сообщение (не группа/канал)
                        chat_type = update["message"]["chat"].get("type", "")
                        
                        # Обрабатываем только личные сообщения (private)
                        if chat_type == "private":
                            process_admin_command(message_text, chat_id)
                        # Игнорируем сообщения из групп и каналов
                
                if data["result"]:
                    last_id = data["result"][-1]["update_id"]
                    requests.get(f"{url}?offset={last_id + 1}")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
