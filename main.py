from fastapi import FastAPI, Request
from typing import Optional
from pydantic import BaseModel, Field
from graph import run_weather_agent_quick

app = FastAPI()

class QueryRequest(BaseModel):
    query: str
    guest_email: Optional[str] = Field("mde.benslimane@gmail.com", description="Optional guest email")

@app.post("/query")
async def query_route(req: QueryRequest):
    result = run_weather_agent_quick(req.query, guest_email=req.guest_email)
    return {"answer": result['final_answer'], "trace": result['trace']}