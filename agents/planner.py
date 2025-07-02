from langchain.schema import HumanMessage
from pydantic import BaseModel
from typing import List
import json
import re
from datetime import datetime
from typing import List, Optional


class PlannerOutput(BaseModel):
    location: str
    date_raw: str
    dates: List[str]
    intent: str
    reasoning_type: str
    is_direct_question: bool
    has_calendar_action: bool
    activity: Optional[str] = None
    constraints: Optional[List[str]] = None

def planner_node(llm):
    def planner_fn(state):
        query = state["messages"]
        today_str = datetime.now().strftime("%Y-%m-%d")
        prompt = f"""
            Aujourd’hui, nous sommes le {today_str}.

            Tu es un assistant intelligent qui extrait les informations météo demandées par l'utilisateur.
            Ta tâche est d’identifier chaque association explicite ou implicite entre une ville et une ou plusieurs dates.

            Retourne une **liste JSON**, chaque élément représentant une **combinaison unique** entre :
            - "location" :  la ville mentionnée (si ce n'est pas mentionné prendre Paris.)
            - "date_raw" (texte de l’utilisateur, ex : "ce week-end", "demain")
            - "dates" (une ou plusieurs dates exactes au format AAAA-MM-JJ)
            - "intent" (voir ci-dessous)

            Les intents météo courantes sont :
            - "rain_check" — si on parle de pluie ou de parapluie
            - "temperature_check" — si on demande s’il fait chaud, froid, etc.
            - "activity_feasibility" — si on parle de randonnée, voyage, promenade, etc.
            - "generic_forecast" — pour une demande météo générale
            - ou autre si nécessaire (à toi de figurer l'intitulé de l'intent)

            - "reasoning_type" : type de raisonnement requis pour comprendre ou répondre, choisir parmi :
                - None
                - "temporal_reasoning"
                - "numerical_reasoning"
                - "geographical_reasoning"
                - "constraint_reasoning"
                - ou autre si nécessaire (à toi de figurer l'intitulé du reasoning_type)

            - "is_direct_question" : If it is a direct question (yes or no question)
            - "has_calendar_action" : Return True If a booking action need to be done.

            Champs optionnels à inclure **si pertinents** :

            - "activity" : texte libre décrivant l’activité que l'utilisateur souhaite planifier (ex : "aller à la plage", "faire un pique-nique ou une rando")
            - "constraints" : liste de contraintes exprimées ou implicites liées à la météo ou à l'activité (ex : ["éviter la pluie", "chercher le jour le plus chaud", "Booker un event à 12am"])


            Important :
            - Si une expression temporelle couvre plusieurs jours (comme "ce week-end", "toute la semaine", "this week" -> la semaine où figure aujorud'hui), retourne **une liste de dates précises** dans `"dates"`.
            - Si plusieurs villes sont mentionnées, crée un objet par couple ville.
            - Si une seul ville est mentionné prendre que cette ville comme location pour tous les éléments.
            - Formate le tout en JSON propre et compact.
            - Si dates est vide, prendre par défaut les dates de la a semaine où figure aujorud'hui.

            Question : "{query}"
            Réponse :
        """

        raw_response = llm.invoke([HumanMessage(content=prompt)]).content
        cleaned_response = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_response.strip(), flags=re.MULTILINE)

        try:
            response_json = json.loads(cleaned_response)
        except Exception:
            return {"error": True, "message": "LLM did not return valid JSON"}

        return {
            "plannification": [
                {
                    "location": entry["location"],
                    "date_raw": entry["date_raw"],
                    "dates": entry["dates"],
                    "intent": entry["intent"],
                    "reasoning_type": entry["reasoning_type"],
                    "is_direct_question": entry["is_direct_question"],
                    "has_calendar_action": entry["has_calendar_action"],
                    **({"activity": entry["activity"]} if "activity" in entry else {}),
                    **({"constraints": entry["constraints"]} if "constraints" in entry else {})
                }
                for entry in response_json
            ]
        }

    return planner_fn


def parse_query(query: str, llm) -> list[PlannerOutput]:
    planner = planner_node(llm)
    state = {"messages": query}
    result = planner(state)

    if "error" in result:
        print(" Erreur planner:", result["message"])
        return []

    return [PlannerOutput(**entry) for entry in result["plannification"]]
