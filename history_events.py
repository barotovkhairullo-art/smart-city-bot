import json
from datetime import datetime

class HistoryEvents:
    def __init__(self, json_file='events_database.json'):
        self.json_file = json_file
        self.events = self.load_events()
    
    def load_events(self):
        """Загрузка событий из JSON файла"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Файл {self.json_file} не найден")
            return {}
        except json.JSONDecodeError:
            print(f"Ошибка чтения файла {self.json_file}")
            return {}
    
    def save_events(self):
        """Сохранение событий в JSON файл"""
        try:
            with open(self.json_file, 'w', encoding='utf-8') as file:
                json.dump(self.events, file, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения файла: {e}")
            return False
    
    def get_events_by_date(self, month, day):
        """Получить события по дате (месяц и день)"""
        date_key = f"{month:02d}{day:02d}"
        return self.events.get(date_key, [])
    
    def get_today_events(self):
        """Получить события на сегодняшнюю дату"""
        today = datetime.now()
        return self.get_events_by_date(today.month, today.day)
    
    def add_event(self, month, day, event_text):
        """Добавить новое событие"""
        date_key = f"{month:02d}{day:02d}"
        if date_key not in self.events:
            self.events[date_key] = []
        
        if event_text not in self.events[date_key]:
            self.events[date_key].append(event_text)
            return True
        return False
    
    def search_events(self, keyword):
        """Поиск событий по ключевому слову"""
        results = {}
        for date_key, events_list in self.events.items():
            matching_events = [event for event in events_list if keyword.lower() in event.lower()]
            if matching_events:
                results[date_key] = matching_events
        return results
    
    def get_all_dates_with_events(self):
        """Получить все даты, для которых есть события"""
        return list(self.events.keys())
    
    def get_events_count(self):
        """Получить общее количество событий"""
        count = 0
        for events_list in self.events.values():
            count += len(events_list)
        return count

# Пример использования
if __name__ == "__main__":
    history = HistoryEvents()
    
    print(f"Всего событий в базе: {history.get_events_count()}")
    print(f"Даты с событиями: {len(history.get_all_dates_with_events())}")
    
    # Получить события на сегодня
    today_events = history.get_today_events()
    if today_events:
        print(f"\nСобытия на сегодня:")
        for event in today_events:
            print(f"- {event}")
    else:
        print("\nНа сегодня событий нет")
    
    # Поиск событий
    search_results = history.search_events("ГЭС")
    if search_results:
        print(f"\nСобытия связанные с ГЭС:")
        for date_key, events in search_results.items():
            print(f"Дата: {date_key[:2]}.{date_key[2:]}")
            for event in events:
                print(f"  - {event}")
