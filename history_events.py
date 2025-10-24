def delete_event(month, day, event_index):
    """Удаляет событие по индексу"""
    try:
        events_db = load_events()
        date_key = f"{month:02d}{day:02d}"
        
        if date_key in events_db and 0 <= event_index - 1 < len(events_db[date_key]):
            deleted_event = events_db[date_key].pop(event_index - 1)
            
            # Если событий не осталось, удаляем дату
            if not events_db[date_key]:
                del events_db[date_key]
            
            save_events(events_db)
            return f"✅ Событие удалено!\n📅 {day:02d}.{month:02d}\n🗑️ {deleted_event}"
        else:
            return "❌ Событие не найдено!"
    except Exception as e:
        return f"❌ Ошибка удаления: {e}"
