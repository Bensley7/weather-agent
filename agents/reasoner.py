from pydantic import BaseModel
from typing import List
from langchain.schema import HumanMessage
import json
import re

class CityAdvice(BaseModel):
    dates: List[str]
    location: str
    summaries: str
    actions: str
    reasons: str
    decision: str

class WeatherIntentData(BaseModel):
    forecast: dict
    plan: dict

def reasoner_node(llm):
    def reasoner_fn(state):
        forecasts: List[dict] = state.get("forecasts", [])
        plans: List[dict] = state.get("plannification", [])

        weather_intent_data = [
            WeatherIntentData(forecast=forecast, plan=plan).dict()
            for forecast, plan in zip(forecasts, plans)
        ]
        prompt = f"""
        You are a weather reasoning assistant.

        The user has made the following queries, intentions, activities and constraints associated with weather related data:
        {json.dumps(weather_intent_data, indent=2)}

        For each city, and for the dates mentioned in both the planner and forecast:
        - Use the intent, activity, reasoning_type and constraints to guide your reasoning.
        - Provide a high-level summary of the weather.
        - Return a decision:
            - if is_direct_quesion is a yes -> Give a decision like yes it will rain according to the intent
            - else return ""
        - Suggest appropriate actions for example "Bring an umbrella and a warm coat." or "Highest temperature is 30C in Monday".
        - Explain why with evidence from the forecast.

        Output a JSON list in this format:
        [
            {{
                "location": "Paris",
                "dates": ["2025-06-24"],
                "summaries": "It will rain heavily and the max temperature is 20°C.",
                "actions": "Bring an umbrella and a warm coat.",
                "reasons": "80% chance of rain and max temp of 20°C according to forecast."
                "decision": "Yes il will rain"
            }}
        ]

        Note:
        - For each city (location) we get one and only json element in the list
        - If the reasoning_type is like constraint_reasoning please concentrate more on answering the intent based on constraints.
        - if the intent is related to activity_feasability plase focus on activity in yout reasoning.
        """

        response = llm.invoke([HumanMessage(content=prompt)]).content
        cleaned_response = re.sub(r"^```(?:json)?\s*|\s*```$", "", response.strip(), flags=re.MULTILINE)

        try:
            data = json.loads(cleaned_response)
            advisories = [CityAdvice(**entry) for entry in data]
        except Exception as e:
            return {"error": True, "message": f"Failed to parse LLM reasoning: {e}"}

        return {
            "reasoning_result": [advisory.dict() for advisory in advisories]
        }

    return reasoner_fn
