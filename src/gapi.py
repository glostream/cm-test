import os.path
import pandas as pd

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build


class Gapi:
    master_id = "1ILwJH151U3ceilZHZ5xyrYt45gtC-Are7XD3jqhzwiA"
    mlk_id = "1niZajsppNeHSa_lAcaO8Nd_iLytWWcEuTO5JdyhYN2U"

    def __init__(self) -> None:
        self.ranges = {
            Gapi.master_id: ["Main Pipeline", "Settings"],
            Gapi.mlk_id: [
                "Template Test",
                "Cerebro - Raw 1",
                "Cerebro - Raw 2",
                "Cerebro - Final",
                "Keepa - Final",
            ],
        }
        keys = {"token": "keys/token.json", "credentials": "keys/credentials.json"}
        creds = self.authenticate(keys)
        self.api = build("sheets", "v4", credentials=creds)
        # drive_service = build("drive", "v3", credentials=creds)

    def authenticate(self, keys):
        # If modifying these scopes, delete the file token.json.
        scopes = [
            # "https://www.googleapis.com/auth/drive.metadata.readonly",
            "https://www.googleapis.com/auth/spreadsheets",
        ]
        key, credentials = keys.values()
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(key):
            creds = Credentials.from_authorized_user_file(key, scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials, scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(key, "w") as token:
                token.write(creds.to_json())
        return creds

    def get_spreadsheet(self, spreadsheet_id):
        print(f"Getting spreadsheet with id: {spreadsheet_id}...")
        sheet = self.api.spreadsheets()
        try:
            result = (
                sheet.values()
                .batchGet(
                    spreadsheetId=spreadsheet_id, ranges=self.ranges[spreadsheet_id]
                )
                .execute()
            )
            return [pd.DataFrame(v['values']) for v in result.get("valueRanges", [])]
        except Exception as e:
            print(f"An error occurred: {e}")
        return []

    def create_spreadsheet(self, spreadsheet):
        try:
            spreadsheet = (
                self.api.spreadsheets()
                .create(body=spreadsheet, fields="spreadsheetId")
                .execute()
            )
            print("Spreadsheet ID: {0}".format(spreadsheet.get("spreadsheetId")))
        except Exception as e:
            print(f"Could not create spreadsheet: {e}")
