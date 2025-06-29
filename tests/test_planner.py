import os
from pprint import pprint

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_openai import ChatOpenAI

from agents.planner import parse_query, PlannerOutput

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

test_queries = [
    "Quel est le jour le plus chaud de la semaine à Marseille ?",
    "Est-ce qu’il pleuvra demain à Paris ?",
    "Quand pourrais-je faire une balade sans pluie à Lyon cette semaine ?",
    "Prévois-tu du beau temps ce week-end à Bordeaux ?"
]

for i, query in enumerate(test_queries, 1):
    print(f"\n🔎 Query {i}: {query}")
    outputs = parse_query(query, llm)
    if not outputs:
        print("⚠️ No planner output.")
    else:
        for plan in outputs:
            pprint(plan.dict(), sort_dicts=False)
