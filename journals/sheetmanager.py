from __future__ import print_function

import os.path

from journals.exceptions import *
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.

class SpreadsheetManager(object):

    def __init__(self, table=None, sheetid=None, tokenfile='./token.json', credsfile='./credentials.json'):
        self.table = table
        self.creds = None
        self.service = None
        self.sheetid = sheetid
        self.sheet = None
        self.sheetprops = None
        self.tokenfile = tokenfile
        self.credsfile = credsfile
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        try:
            self._authorize()
        except Exception as err:
            raise InitSheetManagerException(err)


    def _authorize(self):
        '''
        The file token.json stores the user's access and refresh tokens, 
        and is created automatically when the authorization flow completes
        for the first time.
        '''
        try:
            if os.path.exists(self.tokenfile):
                self.creds = Credentials.from_authorized_user_file(self.tokenfile, self.scopes)
            # If there are no (valid) credentials available, let the user log in.
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credsfile, self.scopes)
                    self.creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(self.tokenfile, 'w') as token:
                    token.write(self.creds.to_json())
        except Exception as err:
            raise AuthSheetManagerException(err)


    def get_sheet_prop(self):
        try:
            # Create connection to Google
            self.service = build('sheets', 'v4', credentials=self.creds, cache_discovery=False)

            # Call the Sheets API
            self.sheet = self.service.spreadsheets()

        except Exception as err:
            raise GoogleConnectionException(err)
        else:
            if not self.sheetid:
                # Create a sheet on google
                try:
                    newsheet = {"properties": {"title": self.table}}
                    request = self.sheet.create(body=newsheet)
                    self.sheetprops = request.execute()
                    self.sheetid = self.sheetprops['spreadsheetId']
                except Exception as err:
                    raise CreateSheetException(err)
            else:
                # Load a sheet from google
                try:
                    request = self.sheet.get(spreadsheetId=self.sheetid)
                    self.sheetprops = request.execute()
                except Exception as err:
                    raise LoadSheetException(err)
            return self.sheetprops


