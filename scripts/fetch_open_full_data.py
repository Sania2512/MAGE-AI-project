import requests
from datetime import datetime

def get_full_open_data():
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": 46.58,
        "lon": 0.34,
        "exclude": "",
        "units": "metric",
        "appid": "112f0318e4939329bbbc221a79895cd6"
    }

    r = requests.get(url, params=params)
    data = r.json()

    result = {
        "current": {
            "timestamp": datetime.fromtimestamp(data["current"]["dt"]).strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": data["current"]["temp"],
            "pressure": data["current"]["pressure"],
            "humidity": data["current"]["humidity"],
            "wind_speed": data["current"]["wind_speed"],
            "uvi": data["current"]["uvi"],
            "weather": data["current"]["weather"][0]["description"]
        },
        "hourly_forecast": [],
        "daily_forecast": []
    }

    # Prévisions horaires (prochaines 48h)
    for hour in data["hourly"][:48]:
        result["hourly_forecast"].append({
            "time": datetime.fromtimestamp(hour["dt"]).strftime("%Y-%m-%d %H:%M:%S"),
            "temp": hour["temp"],
            "pressure": hour["pressure"],
            "humidity": hour["humidity"],
            "wind_speed": hour["wind_speed"],
            "weather": hour["weather"][0]["description"]
        })

    # Prévisions journalières (jusqu’à 7 jours)
    for day in data["daily"]:
        result["daily_forecast"].append({
            "date": datetime.fromtimestamp(day["dt"]).strftime("%Y-%m-%d"),
            "temp_day": day["temp"]["day"],
            "temp_night": day["temp"]["night"],
            "pressure": day["pressure"],
            "humidity": day["humidity"],
            "wind_speed": day["wind_speed"],
            "weather": day["weather"][0]["description"]
        })

    return result