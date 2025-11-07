import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# Configurações OAuth
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "seu-client-id")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "seu-client-secret")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8888/api/v1/auth/google/callback")

# Scopes expandidos para incluir Calendar
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events'
]

def get_google_oauth_flow():
    """Retorna o fluxo OAuth do Google com Calendar"""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI]
            }
        },
        scopes=SCOPES
    )
    flow.redirect_uri = REDIRECT_URI
    return flow


def get_calendar_service(access_token: str):
    """Retorna o serviço do Google Calendar"""
    credentials = Credentials(token=access_token)
    service = build('calendar', 'v3', credentials=credentials)
    return service
