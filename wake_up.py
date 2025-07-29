import requests
import datetime

# URL твоего сайта
url = 'https://checklistttavel.onrender.com'

try:
    response = requests.get(url)
    print(f"[{datetime.datetime.now()}] Сайт пробуждён, статус: {response.status_code}")
except Exception as e:
    print(f"[{datetime.datetime.now()}] Ошибка: {e}")
