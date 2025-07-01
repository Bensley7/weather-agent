import sys, os
import json
import re

from pydantic import BaseModel, Field
from typing import List, Optional
import ast 

from langchain.schema import HumanMessage

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.google_calendar import create_events

DEFAULT_GUEST_EMAIL = os.getenv("DEFAULT_GUEST_EMAIL", "mde.benslimane@gmail.com")

class EventDateTime(BaseModel):
    dateTime: str  # ISO 8601 string
    timeZone: str  # e.g., "Europe/Paris"

class Attendee(BaseModel):
    email: str

class GoogleCalendarEvent(BaseModel):
    summary: str
    location: str
    description: str
    start: EventDateTime
    end: EventDateTime
    attendees: Optional[List[Attendee]] = Field(default_factory=list)
    reminders: Optional[dict] = Field(default_factory=lambda: {"useDefault": True})

def booking_node(llm):
    def booking_fn(state):
        
        print("Booking node triggered")

        def make_prompt(map_reasoning_result, guest_email=DEFAULT_GUEST_EMAIL):

            reasoning_json = json.dumps(map_reasoning_result, indent=2)
            prompt = f"""
            Tu es un assistant de planification d'événements dans Google Calendar.

            Tu recevras des conseils météorologiques dans un format JSON avec :
            - "dates"
            - "location"
            - "summaries"
            - "actions"
            - "reasons"
            - "has_calendar_action": toujours True.

            Ta tâche :
            Génère une liste Python contenant uniquement les événements Google Calendar, sans aucun texte explicatif avant ou après.

            💥 Important :
            - NE FOURNIS AUCUN COMMENTAIRE NI EXPLICATION.
            - N'inclus PAS de balises ```python.
            - Commence directement par la liste `[` et termine par `]`.
            - Tu dois générer uniquement du JSON valide (double quotes partout), sans aucune explication ni texte autour.

            Exemple attendu :
            [
                {{
                    'summary': 'Sortie plage à Langkawi',
                    'location': 'Langkawi',
                    'description': 'Temps ensoleillé prévu. Parfait pour la plage.',
                    'start': {{
                        'dateTime': '2025-07-05T10:00:00+08:00',
                        'timeZone': 'Asia/Kuala_Lumpur'
                    }},
                    'end': {{
                        'dateTime': '2025-07-05T11:00:00+08:00',
                        'timeZone': 'Asia/Kuala_Lumpur'
                    }},
                    'attendees': [{{'email': '{guest_email}'}}],
                    'reminders': {{'useDefault': True}}
                }}
            ]

            Voici le JSON à interpréter :
            {reasoning_json}
            """

            return prompt

        advisories = state.get("reasoning_result", [])

        bookings = []
        for a in advisories:
            if a.get("has_calendar_action"):
                prompt = make_prompt(a)
                raw_response = llm.invoke([HumanMessage(content=prompt)]).content
                cleaned_response = ast.literal_eval(raw_response)
                try:
                    this_bookings = [GoogleCalendarEvent(**event) for event in cleaned_response]
                    bookings.extend(this_bookings)
                except Exception as e:
                    return {"error": True, "message": f"Failed to parse LLM reasoning: {e}"}

        create_events(bookings)

        return {"booking_events": [booking.dict() for booking in bookings]}

    return booking_fn
