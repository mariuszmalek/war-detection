import os
import gspread

from dotenv import load_dotenv

load_dotenv()

class GoogleSpreadsheet():
    def post(self):
        
        sa = gspread.service_account(filename='./config/war-detection-2927522c3758.json')
        sh = sa.open("War detection")

        wks = sh.worksheet("Planes data")
        # records = wks.get_all_records()
        # values = wks.get_all_values()
        
        wks.update('A3', 'Anthony')