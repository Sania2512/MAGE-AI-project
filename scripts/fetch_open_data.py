import requests

def get_open_data():
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": 46.58,                  # Latitude de Poitiers
        "lon": 0.34,                   # Longitude de Poitiers
        "exclude": "minutely,alerts",  # On exclut les données inutiles pour alléger la réponse
        "units": "metric",             # Température en °C, pression en hPa
        "appid": "112f0318e4939329bbbc221a79895cd6"        # Ta clé API personnelle
    }
    r = requests.get(url, params=params)
    data = r.json()
    return {
        "temperature": data["current"]["temp"],
        "pressure": data["current"]["pressure"]
    }