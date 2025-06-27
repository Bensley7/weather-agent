import requests
import os
import sqlite3
from dotenv import load_dotenv
from datetime import datetime
from dateparser import parse
from pydantic import BaseModel
from typing import List

class Forecast(BaseModel):
    location: str
    dates: list[str]
    conditions: list[str]
    rain_probs: list[float]
    temp_mins: list[float]
    temp_maxs: list[float]
    temperatures: list[float]
    intent: str

load_dotenv()

#WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_KEY = "33b15628c3774643b7b233910252405"
WEATHER_API_KEY_0 = "6539e567b4bf46c98eb173830252306"
DB_PATH = "weather_cache.db"


def classify_date(date_str: str) -> str:
    today = datetime.now().date()
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    if date_obj < today:
        return "past"
    elif date_obj == today:
        return "today"
    else:
        return "future"

# Setup DB if not exists
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            location TEXT,
            date TEXT,
            condition TEXT,
            rain_prob INTEGER,
            temp_min REAL,
            temp_max REAL,
            temperature REAL,
            retrieved_at TEXT,
            PRIMARY KEY (location, date)
        )""")

init_db()


def weather_node():

    def weather_fn(state):

        locations = [k.get("location")for k in state.get("plannification", [])]
        dates = [k.get("dates")for k in state.get("plannification", [])]
        intents = [k.get("intent")for k in state.get("plannification", [])]

        results = []
        for idx in range(len(locations)) :
            intent = intents[idx]
            location = locations[idx]
            intent = intents[idx]
            conditions = []
            rain_probs = []
            temp_mins = []
            temp_maxs = []
            temperatures = []   
            dts = dates[idx]         
            for date in dts:
                class_date = classify_date(date)
                try:
                    # 1. Try cache
                    with sqlite3.connect(DB_PATH) as conn:
                        row = conn.execute(
                            "SELECT condition, rain_prob, temp_min, temp_max, temperature FROM weather WHERE location = ? AND date = ?",
                            (location, date)).fetchone()
                    if row:
                        conditions.append(row[0])
                        rain_probs.append(row[1])
                        temp_mins.append(row[2])
                        temp_maxs.append(row[3])
                        temperatures.append(row[4])
                        print(f"[CACHE] Found cached result for {location} on {date}")
                        continue
                    # 2. Fetch from API
                    if class_date != "past":
                        url = f"http://api.weatherapi.com/v1/forecast.json?q={location}&key={WEATHER_API_KEY_0}&days=3"
                        res = requests.get(url)
                        if res.status_code != 200:
                            raise ValueError(f"Weather API failed for {location}")

                        data = res.json()
                        forecast_day = next((f for f in data["forecast"]["forecastday"] if f["date"] == date), None)
                        if not forecast_day:
                            raise ValueError(f"No forecast for {date} in {location}")

                        condition = forecast_day["day"]["condition"]["text"]
                        rain_prob = forecast_day["day"].get("daily_chance_of_rain", 0)
                        temp_min = forecast_day["day"]["mintemp_c"]
                        temp_max = forecast_day["day"]["maxtemp_c"]
                        temperature = (2*temp_max + temp_min) / 3
                    else:
                        url = (
                            f"http://api.worldweatheronline.com/premium/v1/past-weather.ashx"
                            f"?key={WEATHER_API_KEY}&q={location}&format=json&date={date}&enddate={date}&tp=24"
                        )
                        response = requests.get(url)
                        if response.status_code != 200:
                            raise ValueError(f"Weather API failed for {location}")
                        data = response.json()
                        forecast_day = False
                        dt = data["data"]["weather"][0]
                        condition = dt["hourly"][0]["weatherDesc"][0]["value"]
                        rain_prob = float(dt["hourly"][0]["precipMM"])/200
                        temp_min = float(dt["mintempC"])
                        temp_max = float(dt["maxtempC"])
                        temperature = (2*temp_max + temp_min) / 3

                    conditions.append(condition)
                    rain_probs.append(rain_prob)
                    temp_mins.append(temp_min)
                    temp_maxs.append(temp_max)
                    temperatures.append(temperature)

                    with sqlite3.connect(DB_PATH) as conn:
                        conn.execute("""
                            INSERT OR REPLACE INTO weather (
                                location, date, condition, rain_prob, temp_min, temp_max, temperature, retrieved_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                            (location, date, condition, rain_prob, temp_min, temp_max, temperature, datetime.now().isoformat()))
                        print(f"[API] Fetched new result for {location} on {date}")

                except Exception as e:
                    conditions.append("error")
                    rain_probs.append(-1)
                    temp_mins.append(-999.0)
                    temp_maxs.append(-999.0)
                    temperatures.append(-999.0)

            results.append(Forecast(
                location=location,
                dates=dts,
                conditions=conditions,
                rain_probs=rain_probs,
                temp_mins=temp_mins,
                temp_maxs=temp_maxs,
                temperatures=temperatures,
                intent=intent,
            ))

        return {"forecasts": [r.dict() for r in results]}

    return weather_fn
