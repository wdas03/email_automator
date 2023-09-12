from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailAPI:
    def __init__(self, reauthenticate=True):
        self.service = self.authenticate_user(reauthenticate)

    @staticmethod
    def authenticate_user(reauthenticate=True):
        """Shows basic usage of the Gmail API.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if not reauthenticate:
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            # Call the Gmail API
            service = build('gmail', 'v1', credentials=creds)
            
            return service

        except HttpError as error:
            # TODO(developer) - Handle errors from gmail API.
            print(f'An error occurred: {error}')

            return None

    def list_drafts(self):
        try:
            results = self.service.users().drafts().list(userId='me').execute()
            drafts = results.get('drafts', [])

            if not drafts:
                print('No drafts found.')
                return
            
            # print('Drafts:')
            # for draft in drafts:
            #     print(draft['id'])
            
            return drafts

        except HttpError as error:
            print(f'An error occurred: {error}')