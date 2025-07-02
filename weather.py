import requests

def get_weather(city, lang="ru", api_key="71a2706f703b4dcdbcf125605252206"):
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&lang={lang}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "temp": f"{data['current']['temp_c']}°C",
                "description": data['current']['condition']['text'],
                "icon": data['current']['condition']['icon']
            }
    except Exception as e:
        print("Ошибка погоды:", e)
    return {
        "temp": "Н/Д",
        "description": "Погода недоступна"
    }
