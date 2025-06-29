import os
import sys
from pprint import pprint

# Add project root to path (if needed)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_openai import ChatOpenAI
from graph import build_weather_graph

def run_test_queries_with_trace():
    graph = build_weather_graph()
    for i, query in enumerate(all_test_queries, 1):
        print("=" * 80)
        print(f"🔎 Query {i}: {query}")
        print("-" * 80)
        steps = graph.stream({"messages": query})
        for step in steps:
            for step_name, output in step.items():
                print(f"\n🔸 Step: {step_name}")
                pprint(output)
        print("=" * 80)


llm = ChatOpenAI(model="gpt-4o", temperature=0.3)


# Define all test queries
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

def run_test_queries_with_trace():
    graph = build_weather_graph()
    for i, query in enumerate(all_test_queries, 1):
        print("=" * 80)
        print(f"🔎 Query {i}: {query}")
        print("-" * 80)
        steps = graph.stream({"messages": query})
        for step in steps:
            for step_name, output in step.items():
                print(f"\n🔸 Step: {step_name}")
                pprint(output)
        print("=" * 80)

# Run the test
if __name__ == "__main__":
    run_test_queries_with_trace()


