from pydantic import BaseModel
from typing import List
from langchain.schema import HumanMessage
import json

class CityAdvice(BaseModel):
    dates: List[str]
    location: str
    summaries: list[str]
    actions: List[str]
    reasons: List[str]

class ReasoningResult(BaseModel):
    advisories: List[CityAdvice]

def reasoner_node(llm):
    def reasoner_fn(state):
        forecasts = state.get("forecasts", [])
        prompt = f"""
            You are a weather reasoning assistant.

            Here is the list of cities with their corresponding forecasts weather at specific dates and intents :
            {json.dumps(forecasts, indent=2)}

            The user asked a weather-related question with some intent described above.

            For each city , provide:
            - summaries: List of  intents  value coming from the city forecasts. Each element of the list corresponds to a date.
            - actions: List of what to do depending on the intent . Each element of the list corresponds to a date.
            - reasons: List explain why based on forecast. Each element of the list corresponds to a date

            Return a JSON list like:
            [
            {{
                "location": "Paris",
                "dates": ["2025-06-24"],
                "summaries": ["It will rain heavily / It is 20C"],
                "actions": ["bring_umbrella" / "manteau" / eat ice cream etc.."],
                "reasons": ["High chance of rain in forecast."]
            }}
            ]
        """

        response = llm.invoke([HumanMessage(content=prompt)]).content
        try:
            data = json.loads(response)
            advisories = [CityAdvice(**entry) for entry in data]
            print(advisories)
        except Exception as e:
            return {"error": True, "message": f"Failed to parse LLM reasoning: {e}"}

        return ReasoningResult(advisories=advisories).dict()

    return reasoner_fn
