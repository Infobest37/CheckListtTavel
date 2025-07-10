# generate_destinations_json.py
import json
from data_city import DESTINATION_DATA, Cities

data = {
    "destination_data": DESTINATION_DATA,
    "country_cities": Cities
}

with open("static/data/destinations.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ destinations.json создан в /static/data/")