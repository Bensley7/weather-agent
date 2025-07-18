from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from agents.planner import planner_node
from agents.weather import weather_node
from agents.fallback import fallback_node
from agents.reasoner import reasoner_node
from agents.booking import booking_node
from agents.rewriter import rewriter_node

class WeatherAgentState(TypedDict, total=False):
    messages: str
    plannification: list
    forecasts: list
    reasoning_result: list
    booking_events: list
    ai_writer_result: str
    error: bool
    guest_email: str

llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

def build_weather_graph():
    builder = StateGraph(state_schema=WeatherAgentState)

    builder.add_node("planner", planner_node(llm))
    builder.add_node("weather", weather_node())
    builder.add_node("fallback", fallback_node())
    builder.add_node("reasoner", reasoner_node(llm))
    builder.add_node("booking", booking_node(llm))
    builder.add_node("rewriter", rewriter_node(llm))

    builder.set_entry_point("planner")
    builder.add_edge("planner", "weather")
    builder.add_conditional_edges("weather", lambda x: x.get("error", False), {True: "fallback", False: "reasoner"})
    builder.add_edge("fallback", "reasoner")
    builder.add_conditional_edges(
        "reasoner",
        lambda state: any(a.get("has_calendar_action") for a in state.get("reasoning_result", [])),
        {
            True: "booking",
            False: "rewriter"
        }
    )
    builder.add_edge("booking", "rewriter")
    builder.set_finish_point("rewriter")

    app = builder.compile()

    return app


def run_weather_agent_quick(user_input, guest_email=None):
    app = build_weather_graph()
    inputs = {
        "messages": user_input,
    }
    if guest_email:
        inputs["guest_email"] = guest_email

    final_output = app.invoke(inputs)

    return {"final_answer": final_output["ai_writer_result"], "trace": final_output}
