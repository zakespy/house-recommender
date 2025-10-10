# google_api_source.py
import requests
import time
from  dotenv import load_dotenv
import os

class AmenitiesDataSource:
    def __init__(self, api_key: str):
        self.api_key = os.getenv("API_KEY")
        # self.api_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    def textsearch_api(self,amenities_list,address):
        dictionary = {}
        
        for amenities in amenities_list:
            url = "https://places.googleapis.com/v1/places:searchText"
            text = f"{amenities} in {address}"
            payload = {
                "textQuery" : text
            }
            self.headers['Content-Type'] = "application/json"
            self.headers = {
                "X-Goog-Api-Key": self.api_key,
                # "X-Goog-FieldMask": "*"
                "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.priceLevel"
            }

            response = requests.post(url, headers= self.headers, json= payload)

            if response.status_code == 200:
                dictionary[amenities] = response.json()
            else:
                response.raise_for_status()

        return dictionary
