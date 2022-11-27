import gspread
from django.conf import settings
from oauth2client.service_account import ServiceAccountCredentials


def init_gspread(key=None):
    """Initialize and return the DB
    (optional) key: the key of google spreadsheet. Defaults to Francis DB's key
    """
    if key is None:
        # Francis DB
        key = '1hpF3TVCHIMXXXdeVtHdPgQOCOq1NfqYp71uJ4suQViI'

    # Google Drive API related stuff
    scopes = ['https://spreadsheets.google.com/feeds',
              'https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_dict(settings.GAPI_AUTH_DICT, scopes)
    client = gspread.authorize(credentials)

    db = client.open_by_key(key)

    return db
