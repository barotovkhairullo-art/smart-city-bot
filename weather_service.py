import requests
from datetime import datetime, timedelta

OPENWEATHER_API_KEY = "4591744d1155216c26fd89d0fb349eb7"

def get_working_hours_countdown():
    """Возвращает строку с временем работы и обратным отсчетом"""
    now = datetime.now()
    
    # Время работы: 8:00 - 17:00 Душанбе (UTC+5)
    work_start_dushanbe = 8
    work_end_dushanbe = 17
    
    # Текущее время Душанбе
    current_dushanbe_hour = (now.hour + 5) % 24
    current_dushanbe_minute = now.minute
    
    # Если сейчас до 8:00 Душанбе
    if current_dushanbe_hour < work_start_dushanbe or (current_dushanbe_hour == work_start_dushanbe and current_dushanbe_minute == 0):
        # Считаем до начала рабочего дня (8:00 Душанбе)
        target_hour_utc = (work_start_dushanbe - 5) % 24
        start_time_utc = now.replace(hour=target_hour_utc, minute=0, second=0, microsecond=0)
        if now >= start_time_utc:
            start_time_utc = (now + timedelta(days=1)).replace(hour=target_hour_utc, minute=0, second=0, microsecond=0)
        
        time_left = start_time_utc - now
        hours = time_left.seconds // 3600
        minutes = (time_left.seconds % 3600) // 60
        
        return f"🏢 ГОСУДАРСТВЕННОЕ УНИТАРНОЕ ПРЕДПРИЯТИЕ «УМНЫЙ ГОРОД»\n\n🕐 Время работы: 8:00 - 17:00\n⏳ До начала рабочего дня: {hours}ч {minutes}м\n\n📍 Адрес: г. Душанбе\n📞 Телефон: +992 123 45 67 89"
    
    # Если сейчас рабочее время (8:00 - 17:00 Душанбе)
    elif work_start_dushanbe <= current_dushanbe_hour < work_end_dushanbe:
        # Считаем до конца рабочего дня (17:00 Душанбе)
        target_hour_utc = (work_end_dushanbe - 5) % 24
        end_time_utc = now.replace(hour=target_hour_utc, minute=0, second=0, microsecond=0)
        if now >= end_time_utc:
            end_time_utc = (now + timedelta(days=1)).replace(hour=target_hour_utc, minute=0, second=0, microsecond=0)
        
        time_left = end_time_utc - now
        hours = time_left.seconds // 3600
        minutes = (time_left.seconds % 3600) // 60
        
        return f"🏢 ГОСУДАРСТВЕННОЕ УНИТАРНОЕ ПРЕДПРИЯТИЕ «УМНЫЙ ГОРОД»\n\n🕐 Время работы: 8:00 - 17:00\n⏳ До конца рабочего дня: {hours}ч {minutes}м\n\n📍 Адрес: г. Душанбе\n📞 Телефон: +992 123 45 67 89"
    
    else:
        # После 17:00 - считаем до начала следующего рабочего дня
        target_hour_utc = (work_start_dushanbe - 5) % 24
        start_time_utc = (now + timedelta(days=1)).replace(hour=target_hour_utc, minute=0, second=0, microsecond=0)
        time_left = start_time_utc - now
        hours = time_left.seconds // 3600
        minutes = (time_left.seconds % 3600) // 60
        
        return f"🏢 ГОСУДАРСТВЕННОЕ УНИТАРНОЕ ПРЕДПРИЯТИЕ «УМНЫЙ ГОРОД»\n\n🕐 Время работы: 8:00 - 17:00\n⏳ До начала рабочего дня: {hours}ч {minutes}м\n\n📍 Адрес: г. Душанбе\n📞 Телефон: +992 123 45 67 89"

def get_dushanbe_weather():
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q=Dushanbe,TJ&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            desc = data['weather'][0]['description']
            temp = round(data['main']['temp'])
            humidity = data['main']['humidity']
            
            weather_text = f"🌤️ ПОГОДА В ДУШАНБЕ\n\n"
            weather_text += f"• {desc.capitalize()}\n"
            weather_text += f"• Температура: {temp}°C\n"
            weather_text += f"• Влажность: {humidity}%"
            
            return weather_text
    except:
        return "🌤️ ПОГОДА В ДУШАНБЕ\n• Информация о погоде временно недоступна"
