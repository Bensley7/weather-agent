import os
from pprint import pprint

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_openai import ChatOpenAI

from agents.planner import parse_query, PlannerOutput

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

simple_queries = [
    "Quel temps fera-t-il demain à Paris ?",
    "Va-t-il pleuvoir aujourd’hui à Lyon ?",
    "Quelle température fera-t-il mardi à Marseille ?",
    "Est-ce qu’il fait chaud à Madrid ?",
    "Va-t-il faire beau ce week-end?"
]

intermediate_queries = [
    "Est-ce que je peux faire une rando demain à Grenoble ?",
    "Quel est le jour le plus chaud de la semaine à Séville ?",
    "Fera-t-il plus chaud à Paris ou à Rome ce week-end ?",
    "Quel jour est le moins pluvieux cette semaine à Bordeaux ?",
    "Quel jour choisir pour pique-niquer à Toulouse ?"
]

calendar_queries = [
    "Ajoute une alerte pluie pour vendredi à 9h à Lille.",
    "Planifie une sortie vélo cette semaine à Nantes quand il ne pleut pas.",
    "Quand est-ce que je peux organiser un BBQ ce mois-ci à Nice sans vent fort ?",
    "Ajoute un événement dans mon agenda quand il fera beau à Montpellier."
]

complex_queries = [
    "Pluie demain à Paris et température à Lyon ?",
    "Meilleurs jours pour plage et rando la semaine prochaine à Malaga ?",
    "Est-ce qu’il pleuvra plus à Marseille ou Montpellier, et quel jour est le plus chaud ?",
    "Est-ce qu’il fait plus chaud à Casablanca qu’à Fès en ce moment ? Et demain ?"
]

bonus_calendar_queries = [
    "Préviens-moi s’il pleut le jour de mon événement.",
    "Est-ce que le jour de ma réunion est pluvieux ?",
    "Quel est le meilleur moment cette semaine pour faire une activité de plein air ?"
]

all_test_queries = (
    simple_queries +
    intermediate_queries +
    calendar_queries +
    complex_queries +
    bonus_calendar_queries
)


for i, query in enumerate(all_test_queries, 1):
    print(f"\n🔎 Query {i}: {query}")
    outputs = parse_query(query, llm)
    if not outputs:
        print("⚠️ No planner output.")
    else:
        for plan in outputs:
            pprint(plan.dict(), sort_dicts=False)
