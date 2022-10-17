import os
import gspread

from dotenv import load_dotenv

load_dotenv()

class GoogleSpreadsheet():
    def post(self):
        
        creds = None
        
        if os.path.exists('./config/war-detection-2927522c3758.json'):
            creds = Credentials.from_authorized_user_file('./config/war-detection-2927522c3758.json', SCOPES)
         
        if creds:   
            sa = gspread.service_account()
            sh = sa.open("War detection")

            wks = sh.worksheet("Planes data")
            # records = wks.get_all_records()
            # values = wks.get_all_values()
            
            wks.update('A3', 'Anthony')