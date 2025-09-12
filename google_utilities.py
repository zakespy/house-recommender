import os
import requests
from dotenv import load_dotenv

load_dotenv()

class Google_utilities:
    
    
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        self.place_base = os.getenv("GOOGLE_PLACE_BASE")
        self.headers = {
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "*"
        }
        
     
    def get_place_details(self, place_id):
        url = f"{self.place_base}/{place_id}"
        
        response = requests.get(url, headers= self.headers)
        
        if response.status_code  == 200:
            return response.json()
        else:
            response.raise_for_status()   


    def type_search(self, text):
        url = f"{self.place_base}:searchText"
        
        payload = {
            "textQuery" : text
        }
        self.headers['Content-Type'] = "application/json"
        
        response = requests.post(url, headers= self.headers, json= payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


if __name__ == "__main__":
    google_util = Google_utilities()
        
    print(google_util.type_search("College in govindpuri"))