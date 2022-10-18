import os
import gspread

from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class GoogleSpreadsheet():
    
    # Function for Client
    def client(self):
        sa = gspread.service_account(filename='./config/war-detection-2927522c3758.json')
        sh = sa.open("War detection")

        wks = sh.worksheet("Planes data")
        
        return wks
    
    # Function for post data to sheet
    def post(self, num):
        
        count = "{0}".format(num)
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        
        wks = self.client()
        
        next_row = self.next_available_row(wks)
        
        wks.update('A' + str(next_row), count)
        wks.update('B' + str(next_row), date_time)
           
    # Function for getting last value of planes count
    def last_planes_count(self):
        wks = self.client()
        next_row = self.next_available_row(wks)
        value = wks.get('A' + str(next_row - 1)).first()
        
        return value
         
    # Function for take next available row
    def next_available_row(self, worksheet):
        str_list = list(filter(None, worksheet.col_values(1)))
        return len(str_list) + 1