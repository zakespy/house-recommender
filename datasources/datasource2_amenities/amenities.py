# google_api_source.py
import requests
import time
from  dotenv import load_dotenv
import os

load_dotenv()

class AmenitiesDataSource:
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        # self.api_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    def textsearch_api(self, amenity, address):
        url = "https://places.googleapis.com/v1/places:searchText"
        text = f"{amenity} in {address}"
        
        # print(text)
        payload = {
            "textQuery": text
        }
        
        # Define the headers dictionary completely here
        headers = {
            "X-Goog-Api-Key": self.api_key,
            "Content-Type": "application/json", # This is optional but good practice to include
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.priceLevel"
        }

        # Pass the headers dictionary to the request
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            results = response.json().get("places", [])
            # print(response.json())
            
        else:
            print(f"Error: {response.status_code}")
            print(response.text) # Print error details from the API
            response.raise_for_status()

        return len(results)

        
        
if __name__ == "__main__":
    amenitydatasource = AmenitiesDataSource()
    
    amenitydatasource.textsearch_api("hospital","mahavir palace bldg-15, ramdev park")
