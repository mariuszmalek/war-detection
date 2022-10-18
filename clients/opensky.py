import os
import requests

from dotenv import load_dotenv

load_dotenv()

providers = ["RYR", "LOT", "ENT", "RYS", "WZZ", "NSZ", "AUA"]
famous_persons = []

class OpenskyClient():

    def detect(self):
        
        collection = self.fetch()
        
        data = []
        icao_list = []
        
        if collection != None:
            for i in range(len(collection)):
                item = collection[i]
                # only when icao is
                numb = item[0].replace(" ", "")
                icao = item[1].replace(" ", "")
                # if not any(x in icao for x in providers):
                # if all(x in numb for x in famous_persons):
                #     print("We found famous person")
                    
                if icao and all(x not in icao for x in providers):
                    # north = 0
                    # Detect if code is in special list*
                    position = item[10]
                    # if position > 60:
                    data.append(item)
                    icao_list.append(icao)
        
        return [data, icao_list]
    

    def fetch(self):
        
        options = []
        url_data = None
        
        # Cords near war
        lon_min,lat_min = 12,45 #Finland
        lon_max,lat_max = 28,68 #Italy
        
        url_data = 'https://' + os.getenv('USER_NAME') + ':' + os.getenv('USER_PASSWORD') + '@opensky-network.org/api/states/all?lamin='+str(lat_min)+'&lomin='+str(lon_min)+'&lamax='+str(lat_max)+'&lomax='+str(lon_max)
        response = requests.get(url_data).json()

        return response['states']
