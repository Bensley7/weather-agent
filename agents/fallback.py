def fallback_node():
    def fallback_fn(state):
        location = state.get("location", "unknown")
        date = state.get("date", "unknown")
        return {
            "forecasts": [
                {
                    "location": location,
                    "date": date,
                    "condition": "unknown",
                    "rain_prob": -1,
                    "source": "fallback"
                }
            ]
        }
    return fallback_fn