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
├── tests/
├── .env
├── main.py
├── graph.py
├── requirements.txt
└── README.md
```

---

##  Quickstart

### 1.  Installation

```bash
git clone git@github.com:Bensley7/weather-agent.git
cd weather-agent
```

### 2. Create & activate your environment
```bash
conda create -n weather-agent python=3.10
conda activate weather-agent
```


### 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4.  Setup your .env
Create a .env file in the root directory:

```text
OPENAI_API_KEY=your_openai_key
DEFAULT_GUEST_EMAIL=you@example.com
WEATHER_API_KEY_HISTORY="xxxxxxxxxxxxxxxxxxx"
WEATHER_API_KEY_FORECAST="xxxxxxxxxxxxxxxxxxxx"
WEATHER_DB_PATH="/tmp/weather_cache.db"
```

#### How to Get API Keys WEATHER_API_KEY_FORECAST

- Visit: https://www.weatherapi.com/

- Create a free account

- After verifying your email, go to My Account → API Keys

- Copy your API key and paste it in the .env file

- It can predict only 3 days including the present.

#### How to Get API Keys WEATHER_API_KEY_HISTORY

- Visit: https://www.worldweatheronline.com/developer/

- Register for a free or premium account

- After logging in, go to My Account → API Keys

- Copy your key and add it to the .env file