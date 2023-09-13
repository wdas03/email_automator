from __future__ import print_function
from email.mime.multipart import MIMEMultipart

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from email.mime.text import MIMEText
import base64

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.modify']


class GmailAPI:
    def __init__(self, client_id, client_secret, redirect_uri_port):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri_port = redirect_uri_port

        self.flow = self.create_flow()

        # self.service = self.authenticate_user(client_id, client_secret, redirect_uri_port, reauthenticate=reauthenticate)

    def create_flow(self):
        flow = Flow.from_client_config(
            client_config={
                "installed": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uris": [f"http://localhost:{self.redirect_uri_port}"],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
                }
            },
            scopes=SCOPES,
            redirect_uri = f"http://localhost:{self.redirect_uri_port}"
        )

        return flow

    def get_authentication_url(self):
        """Get the URL for the OAuth2 flow."""
        return self.flow.authorization_url()[0]

    def get_access_token(self, code):
        """Get the access token from the OAuth2 flow."""
        return self.flow.fetch_token(code=code)

    def get_credentials(self, code):
        """Get the credentials from the OAuth2 flow."""
        _ = self.flow.fetch_token(code=code)

        return self.flow.credentials

    def build_service(self, code):
        self.service = build('gmail', 'v1', credentials=self.get_credentials(code))

    def authenticate_user_desktop(self, reauthenticate=True):
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
                # flow = InstalledAppFlow.from_client_secrets_file(
                #     'credentials.json', SCOPES)
                # creds = flow.run_local_server(port=0)
                # Create OAuth2 flow
                flow = InstalledAppFlow.from_client_config(
                    client_config={
                        "installed": {
                            "client_id": self.client_id,
                            "client_secret": self.client_secret,
                            "redirect_uris": [f"http://localhost:{self.redirect_uri_port}"],
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
                        }
                    },
                    scopes=SCOPES,
                    redirect_uri = f"http://localhost:{self.redirect_uri_port}"
                )

                # Run local server for OAuth2 flow
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            # Call the Gmail API
            service = build('gmail', 'v1', credentials=creds)
            self.service = service

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
    
    def create_message(self, sender, sender_name, to, subject, message_text):
        """Create a MIME Text message with a custom sender name."""
        msg = MIMEMultipart()
        msg['to'] = to
        msg['from'] = f"{sender_name} <{sender}>"
        msg['subject'] = subject

        msg.attach(MIMEText(message_text, 'plain'))

        raw_message = base64.urlsafe_b64encode(msg.as_string().encode('utf-8'))
        return {'raw': raw_message.decode('utf-8')}

    def send_message(self, user_id, message):
        """Send an email message."""
        try:
            message = self.service.users().messages().send(userId=user_id, body=message).execute()
            print(f"Message Id: {message['id']}")
            return message
        except HttpError as error:
            print(f"An error occurred: {error}")

    def send_individual_email(self, sender, to, subject, message_text):
        """Send an individual email."""
        message = self.create_message(sender, to, subject, message_text)
        self.send_message("me", message)

    def send_mass_email(self, sender, recipients, subject, message_text):
        """Send a mass email to multiple recipients."""
        for recipient in recipients:
            self.send_individual_email(sender, recipient, subject, message_text)
    
    def create_reply_message(self, parent_message, sender, subject, message_text):
        """Create a MIME Text message for replying to an existing thread."""
        msg = MIMEMultipart()
        msg['To'] = parent_message['from']
        msg['From'] = sender
        msg['Subject'] = subject
        msg['In-Reply-To'] = parent_message['messageId']
        msg['References'] = parent_message['messageId']

        msg.attach(MIMEText(message_text, 'plain'))

        raw_message = base64.urlsafe_b64encode(msg.as_string().encode('utf-8'))
        return {'raw': raw_message.decode('utf-8'), 'threadId': parent_message['threadId']}

    def reply_to_thread(self, thread_id, sender, subject, message_text):
        """Reply to an existing thread."""
        # Get the last message in the thread
        thread_data = self.service.users().threads().get(userId='me', id=thread_id).execute()
        last_message = thread_data['messages'][-1]
        last_message_data = last_message['payload']['headers']

        parent_message = {}
        for header in last_message_data:
            if header['name'] == 'From':
                parent_message['from'] = header['value']
            if header['name'] == 'Message-ID':
                parent_message['messageId'] = header['value']

        parent_message['threadId'] = thread_id

        # Create the reply message
        message = self.create_reply_message(parent_message, sender, subject, message_text)

        # Send the message
        self.send_message('me', message)