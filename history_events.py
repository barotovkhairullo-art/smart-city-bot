import random
from datetime import datetime
import json

def load_events():
    try:
        with open('events_database.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {
            "1023": ["1991 – В Душанбе открыт первый международный бизнес-центр «Пойтахт»"],
            "1024": ["1929 – Вышел первый номер сатирической газеты «Хорпуштак»"]
        }

def save_events(events_db):
    with open('events_database.json', 'w', encoding='utf-8') as f:
        json.dump(events_db, f, ensure_ascii=False, indent=2)

def add_event(month, day, event_text):
    try:
        events_db = load_events()
        date_key = f"{month:02d}{day:02d}"
        if date_key not in events_db:
            events_db[date_key] = []
        events_db[date_key].append(event_text)
        save_events(events_db)
        return f"✅ Событие добавлено!\n📅 {day:02d}.{month:02d}\n📝 {event_text}"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def delete_event(month, day, event_index):
    try:
        events_db = load_events()
        date_key = f"{month:02d}{day:02d}"
        if date_key in events_db and 0 <= event_index - 1 < len(events_db[date_key]):
            deleted_event = events_db[date_key].pop(event_index - 1)
            if not events_db[date_key]:
                del events_db[date_key]
            save_events(events_db)
            return f"✅ Событие удалено!\n📅 {day:02d}.{month:02d}\n🗑️ {deleted_event}"
        else:
            return "❌ Событие не найдено!"
    except Exception as e:
        return f"❌ Ошибка удаления: {e}"

def get_tajikistan_history():
    try:
        events_db = load_events()
        today = datetime.now()
        date_key = f"{today.month:02d}{today.day:02d}"
        events = events_db.get(date_key, [])
        if events:
            selected_events = random.sample(events, min(3, len(events)))
            months = {
                1: "ЯНВАРЯ", 2: "ФЕВРАЛЯ", 3: "МАРТА", 4: "АПРЕЛЯ", 
                5: "МАЯ", 6: "ИЮНЯ", 7: "ИЮЛЯ", 8: "АВГУСТА",
                9: "СЕНТЯБРЯ", 10: "ОКТЯБРЯ", 11: "НОЯБРЯ", 12: "ДЕКАБРЯ"
            }
            month_name = months.get(today.month, "")
            history_text = f"📜 ДЕНЬ В ИСТОРИИ ТАДЖИКИСТАНА – {today.day} {month_name}\n\n"
            for event in selected_events:
                history_text += f"• {event}\n"
            return history_text
        else:
            general_events = [
                "1991 - Таджикистан провозгласил независимость",
                "2009 - Открыт мост дружбы с Афганистаном"
            ]
            selected = random.sample(general_events, 2)
            months = {
                1: "ЯНВАРЯ", 2: "ФЕВРАЛЯ", 3: "МАРТА", 4: "АПРЕЛЯ", 
                5: "МАЯ", 6: "ИЮНЯ", 7: "ИЮЛЯ", 8: "АВГУСТА",
                9: "СЕНТЯБРЯ", 10: "ОКТЯБРЯ", 11: "НОЯБРЯ", 12: "ДЕКАБРЯ"
            }
            month_name = months.get(today.month, "")
            history_text = f"📜 ДЕНЬ В ИСТОРИИ ТАДЖИКИСТАНА – {today.day} {month_name}\n\n"
            for event in selected:
                history_text += f"• {event}\n"
            return history_text
    except Exception as e:
        return "📜 ДЕНЬ В ИСТОРИИ ТАДЖИКИСТАНА\n• 1991 - Таджикистан провозгласил независимость"
