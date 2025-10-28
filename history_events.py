import json
from datetime import datetime

def load_events():
    try:
        with open('events_database.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_events(events_db):
    try:
        with open('events_database.json', 'w', encoding='utf-8') as f:
            json.dump(events_db, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def get_tajikistan_history():
    try:
        current_date = datetime.now()
        month = current_date.month
        day = current_date.day
        
        date_key = f"{month:02d}{day:02d}"
        events_db = load_events()
        
        if date_key in events_db and events_db[date_key]:
            events = events_db[date_key]
            history_text = f"📜 ДЕНЬ В ИСТОРИИ ТАДЖИКИСТАНА - {day:02d}.{month:02d}\n\n"
            
            for event in events:
                if event.strip():  # Если строка не пустая
                    history_text += f"{event}\n\n"
                else:  # Если пустая строка (разделитель)
                    history_text += "\n"
            
            return history_text.strip()  # Убираем лишние пробелы в конце
        else:
            return f"📜 ДЕНЬ В ИСТОРИИ ТАДЖИКИСТАНА - {day:02d}.{month:02d}\n\nИсторических событий на эту дату не найдено"
    except Exception as e:
        return f"📜 ДЕНЬ В ИСТОРИИ ТАДЖИКИСТАНА\n\nИнформация временно недоступна"

def add_event(month, day, event_text):
    try:
        events_db = load_events()
        date_key = f"{month:02d}{day:02d}"
        
        if date_key not in events_db:
            events_db[date_key] = []
        
        events_db[date_key].append(event_text)
        
        if save_events(events_db):
            return f"✅ Событие добавлено для даты {day:02d}.{month:02d}"
        else:
            return "❌ Ошибка сохранения"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def delete_event(month, day, event_index):
    try:
        events_db = load_events()
        date_key = f"{month:02d}{day:02d}"
        
        if date_key in events_db and 0 <= event_index < len(events_db[date_key]):
            deleted_event = events_db[date_key].pop(event_index)
            
            # Если событий не осталось, удаляем дату
            if not events_db[date_key]:
                del events_db[date_key]
            
            if save_events(events_db):
                return f"✅ Событие удалено: {deleted_event}"
            else:
                return "❌ Ошибка сохранения"
        else:
            return "❌ Событие не найдено"
    except Exception as e:
        return f"❌ Ошибка: {e}"
