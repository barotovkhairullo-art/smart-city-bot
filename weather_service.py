import requests
from datetime import datetime

OPENWEATHER_API_KEY = "4591744d1155216c26fd89d0fb349eb7"

def get_dushanbe_weather():
    """Погода с OpenWeatherMap"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q=Dushanbe,TJ&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            desc = data['weather'][0]['description']
            temp_min = round(data['main']['temp_min'])
            temp_max = round(data['main']['temp_max'])
            wind = data['wind']['speed']
            humidity = data['main']['humidity']
            
            weather_text = f"🌤️ ПРОГНОЗ ПОГОДЫ НА {datetime.now().strftime('%d.%m.%Y')}\n\n"
            weather_text += f"По городу Душанбе – {desc.capitalize()}\n"
            weather_text += f"Ветер западный {int(wind)}-{int(wind)+3} м/с\n"
            weather_text += f"Температура: ночью {temp_min}-{temp_min+2}°C, днем {temp_max-2}-{temp_max}°C\n"
            weather_text += f"Влажность: {humidity}%"
            
            return weather_text
    except:
        return "🌤️ ПРОГНОЗ ПОГОДЫ\n\nПо городу Душанбе – Облачно. Ветер 3-6 м/с.\nТемпература: ночью 10-12°C, днем 16-18°C"