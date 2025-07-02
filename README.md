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
- Google Calendar integration (OAuth2)
- Supports testing mode with cached forecasts
- Handles vague, indirect, or multi-intent prompts
- Keeps credentials out of Git with `.env` support

---

## Project Structure

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
├── credentials/
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

- Create a .env file in the root directory:

```text
OPENAI_API_KEY=your_openai_key
WEATHER_API_KEY_HISTORY="xxxxxxxxxxxxxxxxxxx"
WEATHER_API_KEY_FORECAST="xxxxxxxxxxxxxxxxxxxx"
WEATHER_DB_PATH="/tmp/weather_cache.db"
```

Note that for the optional booking node, integrating an invitation to a calendar needs an email. This email is accessible when a user register or access the web app. The ```DEFAULT_GUEST_EMAIL``` is a way to mock this process.

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

#### Caching Weather forecast or past response

Set ```text WEATHER_DB_PATH="/tmp/weather_cache.db" ``` to use cached forecast responses and avoid repeated API calls.


### 5.  Google Calendar Integration

This agent supports event creation via the Google Calendar API.

To enable it:

- Create OAuth credentials from Google Cloud Console.

- Enable the Calendar API.

- Create ``credentials``` directory in the root of the project.

- Add your token to ```token.json``` in ```credentials``` directory or use the OAuth flow.


### 6.  Run the assistant

- Run:

```bash
uvicorn main:app  --port 9003 --reload
```

- Go to  http://127.0.0.1:9003/docs
- Fill the query with the question
- You can change the port and host

### 7. Key Components:

| Agent      | Role                                                   |
| ---------- | ------------------------------------------------------ |
| `planner`  | Parses the input and detects locations, dates, intents |
| `weather`  | Fetches or caches forecast data                        |
| `reasoner` | Analyzes intent vs. forecast to provide advice         |
| `booking`  | Generates Google Calendar events (if applicable)       |
| `rewriter` | Reformulates the assistant’s final answer              |
| `fallback` | Provides generic response if weather lookup fails      |


