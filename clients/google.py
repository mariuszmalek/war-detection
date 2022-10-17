import os
import gspread

from dotenv import load_dotenv

load_dotenv()

class GoogleSpreadsheet():
    def fetch():
        return 1
    
    def post():
        sa = gspread.service_account()
        sh = sa.open("War detection")

        wks = sh.worksheet("Planes data")
        
        return 1