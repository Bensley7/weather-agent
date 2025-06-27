from langchain.schema import HumanMessage
from dateparser import parse
from pydantic import BaseModel
from typing import List
import json
import re
from datetime import datetime
 
class PlannerOutput(BaseModel):
    location: str
    date_raw: str
    dates: List[str]
    intent: str

def planner_node(llm):
    def planner_fn(state):
        query = state["messages"]
        today_str = datetime.now().strftime("%Y-%m-%d")
        prompt = f"""
            Aujourd’hui, nous sommes le {today_str}.

            Tu es un assistant intelligent qui extrait les informations météo demandées par l'utilisateur.
            Ta tâche est d’identifier chaque association explicite ou implicite entre une ville et une ou plusieurs dates.

            Retourne une **liste JSON**, chaque élément représentant une **combinaison unique** entre :
            - "location" :  la ville mentionnée
            - "date_raw" (texte de l’utilisateur, ex : "ce week-end", "demain")
            - "dates" (une ou plusieurs dates exactes au format AAAA-MM-JJ)
            - "intent" (voir ci-dessous)

            Les intents météo courantes sont :
            - "rain_check" — si on parle de pluie ou de parapluie
            - "temperature_check" — si on demande s’il fait chaud, froid, etc.
            - "activity_feasibility" — si on parle de randonnée, voyage, promenade, etc.
            - "generic_forecast" — pour une demande météo générale

            Important :
            - Si une expression temporelle couvre plusieurs jours (comme "ce week-end", "toute la semaine", "this week" -> la semaine où figure aujorud'hui), retourne **une liste de dates précises** dans `"dates"`.
            - Si plusieurs villes sont mentionnées, crée un objet par couple ville/date.
            - Formate le tout en JSON propre et compact.

            Question : "{query}"
            Réponse :
        """

        raw_response = llm.invoke([HumanMessage(content=prompt)]).content
        cleaned_response = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_response.strip(), flags=re.MULTILINE)

        try:
            response_json = json.loads(cleaned_response)
        except Exception:
            return {"error": True, "message": "LLM did not return valid JSON"}

        return {"plannification" : [PlannerOutput(location=entry["location"], date_raw=entry["date_raw"], dates=entry["dates"], intent=entry['intent']).dict() for entry in response_json]}

    return planner_fn