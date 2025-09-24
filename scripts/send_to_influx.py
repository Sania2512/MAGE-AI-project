from fetch_open_full_data import get_full_open_data
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import time

# Configuration InfluxDB
bucket = "MAGE'AI"
org = "MAGE'AI"
token = "4ry4HbUFXCgOToTwu6NGNDgygnH25Tw3avu2jJlqJ7LY5nxN0CzWs-ZepVBFssBa0OgfIycWiScGsvP1bcj3RA=="
url = "http://localhost:8086"

client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

while True:
    data = get_full_open_data()["current"]

    point = Point("weather") \
        .field("temperature", data["temperature"]) \
        .field("pressure", data["pressure"]) \
        .field("humidity", data["humidity"]) \
        .field("wind_speed", data["wind_speed"]) \
        .field("uvi", data["uvi"]) \
        .tag("location", "Poitiers")

    write_api.write(bucket=bucket, org=org, record=point)
    print("Données envoyées :", data)
    time.sleep(10)