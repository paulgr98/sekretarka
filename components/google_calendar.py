from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime as dt
import os


class GoogleCalendar:
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/calendar.readonly']
        self.creds = None
        self.service = None
        self.__token_path__ = 'token.json'
        self.__credentials_path__ = 'credentials.json'

    def login(self):
        if os.path.exists(self.__token_path__):
            self.creds = Credentials.from_authorized_user_file(self.__token_path__, self.scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.__credentials_path__, self.scopes)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.__token_path__, 'w') as token:
                token.write(self.creds.to_json())
        self.service = build('calendar', 'v3', credentials=self.creds)

    def get_next_event(self):
        now = dt.datetime.utcnow().isoformat() + 'Z'
        events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                                   maxResults=1, singleEvents=True,
                                                   orderBy='startTime').execute()
        events = events_result.get('items', [])
        if not events:
            return None
        else:
            return events
