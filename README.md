# ☀️ Weather Agent (LangGraph + LangChain)

A modular weather assistant powered by [LangGraph](https://github.com/langchain-ai/langgraph), designed to analyze user queries, retrieve weather forecasts, reason over them, and suggest or book activities on Google Calendar.

---

## 🚀 Features

- 🌤️ Interprets natural language weather-related questions.
- 🧠 Uses agents for:
  - Query planning
  - Forecast retrieval
  - Intent reasoning
  - Actionable advice
  - Optional calendar booking
- 📅 Google Calendar integration (OAuth2)
- 🧪 Supports testing mode with cached forecasts
- 🔄 Handles vague, indirect, or multi-intent prompts
- 🔐 Keeps credentials out of Git with `.env` support

---

## 🧱 Project Structure

```text
weather-agent/
├── agents/
│ ├── planner.py
│ ├── weather.py
│ ├── reasoner.py
│ ├── rewriter.py
│ ├── booking.py
│ └── fallback.py
├── utils/
│ ├── google_calendar.py
├── .env
├── main.py
├── requirements.txt
└── README.md