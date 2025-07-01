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
    has_calendar_action: bool

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

        The user has made the following weather-related queries, with associated intentions, activities, and constraints:

        Each item below contains:
        - 'forecast': Weather forecast details for a specific city and dates.
        - 'plan': The user's query analysis with fields like:
            - 'intent': user’s intention (e.g. rain_check, temperature_check, activity_feasibility),
            - 'reasoning_type': type of logic needed,
            - 'is_direct_question': true if a yes/no answer is expected,
            - 'has_calendar_action': true if the user expressed desire to book/schedule something — ⚠️ **you should set `has_calendar_action = true` in your output only if your generated action actually implies calendar usage (e.g. schedule, book)**.
               following queries, intentions, activities and constraints associated with weather related data:
                
        Here is the reasoning input:
        
        {json.dumps(weather_intent_data, indent=2)}


        For each city, and for the dates present in both the forecast and the plan:
        - Use the intent, activity, reasoning_type and constraints to guide your reasoning.
        - Generate the following structured output for each location:

        Fields:
        - "summaries": A concise natural-language summary of the weather condition over the selected days.
        - "decision": If the plan includes a direct yes/no question (`is_direct_question = true`), answer it clearly using the forecast (e.g. "Yes, it will rain", "No, it will be sunny"). Otherwise leave it as an empty string.
        - "actions": Suggest relevant user actions based on intent and forecast (e.g. "Bring a warm coat", "Schedule a beach day at 10am").
        - "reasons": Explain why these actions or decisions are appropriate based on the forecast.
        - "has_calendar_action": 
            - Return `true` **only** if your suggested action implies that something should be added to a calendar (e.g. “Schedule”, “Book”, “Plan for 10am”, “Add to agenda”).
            - If the original plan contains `"has_calendar_action": true`, it means the user *may* want to book something — but do not set `has_calendar_action = true` unless your **generated action** actually confirms it.
            - Otherwise, return `false`.

        Output format (one entry per location only):
        [
        {{
            "location": "Paris",
            "dates": ["2025-06-30", "2025-07-01"],
            "summaries": "The hottest day will be Tuesday with 37.8°C.",
            "actions": "Schedule your picnic at 10am on Tuesday.",
            "reasons": "Tuesday has the highest temperature compared to Monday.",
            "decision": "",
            "has_calendar_action": true
        }}
        ]

        Note:
        - For each city (location) we get one and only json element in the list
        - If the reasoning_type is a constraint_reasoning type, focus on answering the intent based on constraints.
        - if the intent is about activity_feasability, focus on activity in your reasoning.
        - If there is a booking, we will by defaut book at 10 am if it is not assigned.

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
