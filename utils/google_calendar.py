import os
import datetime
import base64
import json

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_calendar_service():
    os.makedirs("credentials", exist_ok=True)
    token_path = os.path.join("credentials", "token.json")
    if not os.path.exists(token_path):
        load_dotenv()
        token_json_b64 = os.getenv("GOOGLE_TOKEN_JSON_B64")
        if token_json_b64:
            token_data = json.loads(base64.b64decode(token_json_b64))
            with open(token_path, "w") as f:
                json.dump(token_data, f)
    creds = None
    credentials_path = os.path.join("credentials", "credentials.json")
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)


def create_events(events):
    service = get_calendar_service()
    for event in events:
        res = service.events().insert(calendarId='primary', body=event.dict(), sendUpdates='all').execute()
        print(f"✅ Événement créé : {res.get('htmlLink')}")

if __name__ == '__main__':
    event = {
        'summary': 'Barbecue au parc',
        'location': 'Parc Monceau, Paris',
        'description': 'Un petit barbecue entre amis au soleil ☀️',
        'start': {
            'dateTime': '2025-07-05T10:00:00+02:00',
            'timeZone': 'Europe/Paris',
        },
        'end': {
            'dateTime': '2025-07-05T12:00:00+02:00',
            'timeZone': 'Europe/Paris',
        },
        'attendees': [
            {'email': 'berradaz967@gmail.com'}
        ],
        'reminders': {
            'useDefault': True,
        },
    }
    create_events([event])
