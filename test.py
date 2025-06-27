from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import json
from datetime import datetime

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)

query = "Quel temps fera-t-il ce week-end à Paris et à Lyon ?"
today_str = datetime.now().strftime("%Y-%m-%d")

prompt = f"""
Aujourd’hui, nous sommes le {today_str}.
...

Question : "{query}"
Réponse :
"""

response = llm.invoke([HumanMessage(content=prompt)]).content
print("LLM Output:", response)
