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
        Tu es un assistant de raisonnement météorologique.

        L'utilisateur a formulé des requêtes liées à la météo, accompagnées d'intentions(intents), d'activités et de contraintes :

        Chaque élément contient :
        - 'forecast' : détails des prévisions météo pour une ville et des dates spécifiques.
        - 'plan' : analyse de la requête utilisateur avec les champs suivants :
            - 'intent' : intention de l’utilisateur (ex. rain_check, temperature_check, activity_feasibility),
            - 'reasoning_type' : type de raisonnement nécessaire,
            - 'is_direct_question' : true si l’utilisateur attend une réponse oui/non,
            - 'has_calendar_action' : true si l’utilisateur a exprimé un désir de planifier ou réserver quelque chose — ⚠️ **tu ne dois renvoyer `has_calendar_action = true` dans ta sortie que si ton action générée implique réellement l’usage d’un agenda ou calendrier (ex. planifier, réserver, programmer)**.

        Voici les données d’entrée à interpréter :

        {json.dumps(weather_intent_data, indent=2)}

        Pour chaque ville, et pour les dates présentes à la fois dans les prévisions (`forecast`) et l’analyse (`plan`) :
        - Utilise l’intention, l’activité, le type de raisonnement et les contraintes pour guider ta réflexion.
        - Génère la sortie structurée suivante pour chaque ville :

        Champs attendus :
        - "summaries" : résumé concis en langage naturel des conditions météo sur les jours sélectionnés.
        - "decision" : si la requête est une question directe (`is_direct_question = true`), réponds clairement en t’appuyant sur la météo (ex : "Oui, il va pleuvoir", "Non, il fera beau"). Sinon, laisse vide.
        - "actions" : suggère des actions pertinentes en lien avec l’intention et les prévisions (ex : "Prendre un manteau chaud", "Planifier une sortie plage à 10h").
        - "reasons" : explique pourquoi ces actions ou décisions sont appropriées selon les prévisions météo.
        - "has_calendar_action" :
            - Retourne `true` **uniquement** si ton action suggérée implique d’ajouter un événement au calendrier (ex. “Planifier”, “Réserver”, “Prévoir à 10h”, “Ajouter à l’agenda”).
            - Si le champ `"has_calendar_action": true` figure dans la requête initiale, cela signifie que l’utilisateur *envisage* une action, mais ne le retourne que si ton action générée le confirme.
            - Sinon, retourne `false`.

        Format de sortie (un élément unique par ville) :
        [
        {{
            "location": "Paris",
            "dates": ["2025-06-30", "2025-07-01"],
            "summaries": "La journée la plus chaude sera mardi avec 37.8°C.",
            "actions": "Planifiez votre pique-nique mardi à 10h.",
            "reasons": "Mardi est plus chaud que lundi.",
            "decision": "",
            "has_calendar_action": true
        }}
        ]

        Remarques :
        - Une seule entrée JSON par ville.
        - Si le `reasoning_type` est de type `constraint_reasoning`, focalise-toi sur les contraintes exprimées pour répondre à l’intention(intent).
        - Si l’intention (intent) est `activity_feasibility`, focalise-toi sur l’activité dans ton raisonnement.
        - Si une réservation est suggérée, par défaut l’heure sera fixée à 10h si aucune heure précise n’est indiquée.
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
