from fastapi import FastAPI, Request
from pydantic import BaseModel
from graph import run_weather_agent_quick

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def query_route(req: QueryRequest):
    result = run_weather_agent_quick(req.query)
    return {"answer": result['final_answer'], "trace": result['trace']}