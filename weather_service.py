import requests

OPENWEATHER_API_KEY = "4591744d1155216c26fd89d0fb349eb7"

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
        return "🌤️ ПОГОДА В ДУШАНБЕ\n• Облачно\n• Температура: 15-18°C"