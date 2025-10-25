import json
from datetime import datetime

def load_events():
    """
    Загружает события из JSON файла
    """
    try:
        with open('events_database.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Ошибка загрузки событий: {e}")
        return {}

def save_events(events_db):
    """
    Сохраняет события в JSON файл
    """
    try:
        with open('events_database.json', 'w', encoding='utf-8') as f:
            json.dump(events_db, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка сохранения событий: {e}")
        return False

def add_event(month, day, event_text):
    """
    Добавляет событие в базу данных
    """
    try:
        events_db = load_events()
        date_key = f"{month:02d}{day:02d}"
        
        if date_key not in events_db:
            events_db[date_key] = []
        
        events_db[date_key].append(event_text)
        
        if save_events(events_db):
            return f"✅ Событие добавлено!\n📅 {day:02d}.{month:02d}\n📝 {event_text}"
        else:
            return "❌ Ошибка сохранения события"
            
    except Exception as e:
        return f"❌ Ошибка: {e}"

def delete_event(month, day, event_index):
    """
    Удаляет событие из базы данных
    """
    try:
        events_db = load_events()
        date_key = f"{month:02d}{day:02d}"
        
        if date_key in events_db and 0 <= event_index - 1 < len(events_db[date_key]):
            deleted_event = events_db[date_key].pop(event_index - 1)
            
            # Удаляем дату если событий не осталось
            if not events_db[date_key]:
                del events_db[date_key]
            
            if save_events(events_db):
                return f"✅ Событие удалено!\n📅 {day:02d}.{month:02d}\n🗑️ {deleted_event}"
            else:
                return "❌ Ошибка сохранения изменений"
        else:
            return "❌ Событие не найдено!"
            
    except Exception as e:
        return f"❌ Ошибка удаления: {e}"

def get_tajikistan_history():
    """
    Возвращает исторические события для текущей даты
    """
    try:
        events_db = load_events()
        today = datetime.now()
        date_key = f"{today.month:02d}{today.day:02d}"
        events = events_db.get(date_key, [])
        
        if not events:
            return "📜 На сегодня исторических событий не найдено"
        
        months = {
            1: "ЯНВАРЯ", 2: "ФЕВРАЛЯ", 3: "МАРТА", 4: "АПРЕЛЯ", 
            5: "МАЯ", 6: "ИЮНЯ", 7: "ИЮЛЯ", 8: "АВГУСТА",
            9: "СЕНТЯБРЯ", 10: "ОКТЯБРЯ", 11: "НОЯБРЯ", 12: "ДЕКАБРЯ"
        }
        
        month_name = months.get(today.month, "")
        history_text = f"📜 ДЕНЬ В ИСТОРИИ ТАДЖИКИСТАНА – {today.day} {month_name}\n\n"
        
        for event in events:
            history_text += f"• {event}\n"
            
        return history_text
        
    except Exception as e:
        print(f"Ошибка получения истории: {e}")
        return "📜 Информация об исторических событиях временно недоступна"
