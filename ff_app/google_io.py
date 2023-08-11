import pandas as pd
import os
import inspect
import logging

from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from oauth2client.service_account import ServiceAccountCredentials

from .config import CONFIG


LOGGER = logging.getLogger(__file__)


class GoogleSheetsReadWrite:
    def __init__(self,
                 spreadsheet_id=None,
                 creds_dir=None):
        """
        """
        self.spreadsheet_id = spreadsheet_id \
            or CONFIG['google']['spreadsheet_id']
        self.creds = self.get_credentials(creds_dir)

        
    def get_credentials(self, creds_dir):
        """
        """
        creds_dir = creds_dir \
            or os.path.expanduser(CONFIG['google']['credentials_path'])
        LOGGER.info("Using credentials directory '%s'", creds_dir)

        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(os.path.join(creds_dir, 'token.json')):
            creds = Credentials.from_authorized_user_file(
                os.path.join(creds_dir, 'token.json'), scopes)
            LOGGER.info("Obtained credentails from existing 'token.json' file")
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                LOGGER.info("Refreshed expired credentials")
            else:
                LOGGER.info("Obtaining a token using credentials stored in 'credentials.json")

                creds = ServiceAccountCredentials.from_json_keyfile_name(
                    os.path.join(creds_dir, 'credentials.json'), scopes) 

                LOGGER.info("Obtained a token using stored credentials")
            # Save the credentials for the next run
            with open(os.path.join(creds_dir, 'token.json'), 'w') as token:
                token.write(creds.to_json())
        return creds

    def read(self, sheet_name, sheet_range):
        """
        """
        range_name = f'{sheet_name}!{sheet_range}'

        service = build('sheets', 'v4', credentials=self.creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=self.spreadsheet_id,
                                    range=range_name).execute()
        values = result.get('values', [])
        LOGGER.info("Read %s rows from %s", len(values), range_name)
        results_df = pd.DataFrame(columns=values[0], data=values[1:])
        return results_df

    def write(self, sheet_name, data):
        """
        """
        assert isinstance(sheet_name, str), \
            "'sheet_name' must be passed as a string"
        assert isinstance(data, pd.DataFrame), \
            "'data' must be passed as a pandas DataFrame"

        sheet_range = 'A:{}'.format(self._get_upper_range_limit(data.shape[1]))
        range_name = f'{sheet_name}!{sheet_range}'

        service = build('sheets', 'v4', credentials=self.creds)
        
        values = [list(x) for x in data.to_records(index=False)]
        body = {'values': values}
        LOGGER.debug("Attempting to write %s rows to %s",
                     len(values), range_name)
        result = service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body).execute()
        LOGGER.info('Appended %s cells to %s',
                    result.get('updates').get('updatedCells'), range_name)

    def _get_upper_range_limit(self, length):
        """
        """
        assert isinstance(length, int), "'length' must be passed as an integer"
        import string
        if length <= 26:
            limit = string.ascii_uppercase[length]
        elif length <= (26 * 26):
            first = string.ascii_uppercase[int(length / 26) - 1]
            last = string.ascii_uppercase[(length % 26) - 1]
            limit = f'{first}{last}'
        else:
            raise ValueError("Data is too large to determine range")
        return limit