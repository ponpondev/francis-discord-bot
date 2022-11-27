# import json
from datetime import datetime

import requests
from django.conf import settings
from gspread.exceptions import APIError
from pytz import timezone

from utils import db as googledrive


class WebSpider:
    def __init__(self, bot, drive_sheet_name):
        self.bot = bot
        self.db = googledrive.init_gspread()
        self.sheet_name = drive_sheet_name
        self.sheet = self.db.worksheet(self.sheet_name)
        self.delay = settings.SPIDER_DELAY

    @classmethod
    def get_content_by_url(cls, url):

        try:
            r = requests.get(url)
        except Exception:
            return None

        if r.status_code == 200:
            return r.content
        else:
            return None

    def form_checking_data(self):
        try:
            records = self.sheet.get_all_records()
        except APIError:
            try:
                self.db = googledrive.init_gspread()
                self.sheet = self.db.worksheet(self.sheet_name)
                records = self.sheet.get_all_records()
            except APIError:
                return None

        checking_data = [(str(record['id']), record['title']) for record in records]

        return checking_data

    def fetch_data(self):
        pass

    @property
    def fetch_dt(self):
        now = datetime.now()
        vn_tz = now.astimezone(timezone('Asia/Ho_Chi_Minh'))
        return vn_tz
