import requests
import os
import sqlite3
from dotenv import load_dotenv
from datetime import datetime
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

load_dotenv()

WEATHER_API_KEY_HISTORY = os.getenv("WEATHER_API_KEY_HISTORY")
WEATHER_API_KEY_FORECAST = os.getenv("WEATHER_API_KEY_FORECAST")
DB_PATH = os.getenv("WEATHER_DB_PATH", "weather_cache.db")
DB_PATH = os.path.abspath(DB_PATH)

def classify_date(date_str: str) -> str:
    now = datetime.now()
    today = now.date()
    target_date_str = datetime.strptime(date_str, "%Y-%m-%d")
    date_obj = target_date_str.date()
    target_datetime = target_date_str.replace(
        hour=now.hour, minute=now.minute, second=now.second, microsecond=0
    )
    target_epoch = int(target_datetime.timestamp())
    if date_obj < today:
        return "past", target_epoch
    elif date_obj == today:
        return "today", target_epoch
    else:
        return "future", target_epoch

# Setup DB if not exists
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
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
            last_epoch INTEGER,
            PRIMARY KEY (location, date, last_epoch)
        )""")

init_db()


def weather_node():

    def weather_fn(state):

        locations = [k.get("location")for k in state.get("plannification", [])]
        dates = [k.get("dates")for k in state.get("plannification", [])]
        intents = [k.get("intent")for k in state.get("plannification", [])]
        reasoning_types = [k.get("reasoning_type")for k in state.get("plannification", [])]
        activity = [k.get("activity")for k in state.get("plannification", [])]
        constraints = [k.get("constraints")for k in state.get("plannification", [])]

        results = []

        for idx in range(len(locations)) :
            location = locations[idx]
            conditions = []
            rain_probs = []
            temp_mins = []
            temp_maxs = []
            temperatures = []   
            dts = dates[idx]         
            for date in dts:
                class_date, last_date_epoch = classify_date(date)
                try:
                    # 1. Try cache
                    if class_date != "today":
                        with sqlite3.connect(DB_PATH) as conn:
                            row = conn.execute("""
                                SELECT condition, rain_prob, temp_min, temp_max, temperature, last_epoch
                                FROM weather
                                WHERE location = ? AND date = ?
                                ORDER BY ABS(last_epoch - ?) ASC
                                LIMIT 1
                            """, (location, date, last_date_epoch)).fetchone()
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
                        url = f"http://api.weatherapi.com/v1/forecast.json?q={location}&key={WEATHER_API_KEY_FORECAST}&days=3"
                        res = requests.get(url)
                        if res.status_code != 200:
                            raise ValueError(f"Weather API failed for {location}")
                        data = res.json()
                        forecast_day = next((f for f in data["forecast"]["forecastday"] if f["date"] == date), None)
                        if not forecast_day:
                            raise ValueError(f"No forecast for {date} in {location}")
                        if class_date == "today":
                            current_data = data["current"]
                            condition = current_data["condition"].get("text", None)
                            rain_prob = current_data.get("precip_mm", 0) / 200
                            temp_min = forecast_day["day"]["mintemp_c"]
                            temp_max = forecast_day["day"]["maxtemp_c"]
                            temperature = current_data["temp_c"]
                            last_updated_epoch = int(current_data["last_updated_epoch"])
                        else:    
                            condition = forecast_day["day"]["condition"]["text"]
                            rain_prob = forecast_day["day"].get("daily_chance_of_rain", 0)
                            temp_min = forecast_day["day"]["mintemp_c"]
                            temp_max = forecast_day["day"]["maxtemp_c"]
                            temperature = (2*temp_max + temp_min) / 3
                            last_updated_epoch = 0
                    else:
                        url = (
                            f"http://api.worldweatheronline.com/premium/v1/past-weather.ashx"
                            f"?key={WEATHER_API_KEY_HISTORY}&q={location}&format=json&date={date}&enddate={date}&tp=24"
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
                        last_updated_epoch = 0

                    conditions.append(condition)
                    rain_probs.append(rain_prob)
                    temp_mins.append(temp_min)
                    temp_maxs.append(temp_max)
                    temperatures.append(temperature)

                    with sqlite3.connect(DB_PATH) as conn:
                        conn.execute("""
                            INSERT OR REPLACE INTO weather (
                                location, date, condition, rain_prob, temp_min, temp_max, temperature, last_epoch
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                            (location, date, condition, rain_prob, temp_min, temp_max, temperature, last_updated_epoch))
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
            ))

        return {"forecasts": [r.dict() for r in results]}

    return weather_fn


def get_forecast(location: str, dates: List[str]) -> Forecast:
    """
    Interface simplifiée pour appeler le weather_node() sur un seul lieu + liste de dates.
    Utile pour tester en dehors du LangGraph.
    """
    state = {
        "plannification": [{
            "location": location,
            "dates": dates,
            "intent": "generic_forecast",
            "reasoning_type": "none"
        }]
    }

    weather_fn = weather_node()
    result = weather_fn(state)
    
    forecasts = result.get("forecasts", [])
    if not forecasts:
        raise ValueError(f"No forecast generated for {location}")

    return Forecast(**forecasts[0])
