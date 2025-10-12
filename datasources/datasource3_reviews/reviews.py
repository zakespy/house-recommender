# google_api_source.py
import requests
import time
from  dotenv import load_dotenv
import os

load_dotenv()

class ReviewsDataSource:
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        # self.api_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    def get_place_id(self,address: str) -> str | None:
        """
        Geocodes an address using Google's Geocoding API and returns the place_id.

        Args:
            address: The street address to geocode.

        Returns:
            The place_id as a string if found, otherwise None.
        """
        # Load the API key from the .env file
        load_dotenv()
        api_key = os.getenv("API_KEY")

        if not api_key:
            print("Error: API_KEY not found in .env file.")
            return None

        # The base URL for the Geocoding API
        base_url = "https://maps.googleapis.com/maps/api/geocode/json"

        # Parameters to be sent with the request
        # 'requests' will automatically handle URL encoding (e.g., spaces to '+')
        params = {
            'address': address,
            'key': api_key
        }

        try:
            # Make the GET request to the API
            response = requests.get(base_url, params=params)
            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status() 

            # Parse the JSON response
            data = response.json()

            # Check the status and extract the place_id
            if data['status'] == 'OK' and data['results']:
                # Get the place_id from the first result
                place_id = data['results'][0]['place_id']
                return place_id
            else:
                print(f"Error geocoding address. Status: {data.get('status')}")
                if data.get('error_message'):
                    print(f"API Error Message: {data['error_message']}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"An error occurred during the API request: {e}")
            return None
        except (KeyError, IndexError):
            # This handles cases where the JSON response format is unexpected
            print("Error: Could not parse 'place_id' from the API response.")
            return None

    def get_reviews_by_place_id(self,place_id: str) -> list[str] | None:
        """
        Fetches details for a given place_id using the Google Places API
        and returns a list of review texts.

        Args:
            place_id: The unique identifier for the place.

        Returns:
            A list of strings, where each string is a review text.
            Returns an empty list if there are no reviews.
            Returns None if an error occurs.
        """
        # Load the API key from the .env file
        load_dotenv()
        api_key = os.getenv("API_KEY")

        if not api_key:
            print("Error: API_KEY not found in .env file.")
            return None

        # Construct the API URL
        url = f"https://places.googleapis.com/v1/places/{place_id}"

        # Define the headers, including the API key and the crucial FieldMask.
        # The FieldMask tells Google exactly which data fields you want back.
        # This is required for the Places API (New).
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': api_key,
            'X-Goog-FieldMask': 'reviews.text'  # We only ask for the text of the reviews
        }

        try:
            response = requests.get(url, headers=headers)
            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status()

            data = response.json()

            review_texts = []
            # Safely access the 'reviews' list using .get() to avoid errors
            # if the key doesn't exist (e.g., place has no reviews).
            reviews_list = data.get('reviews', [])

            if not reviews_list:
                print("This place has no reviews.")
                return []

            for review in reviews_list:
                # Safely get the text object, and then the text content
                text_object = review.get('text', {})
                if text_object and 'text' in text_object:
                    review_texts.append(text_object['text'])

            return review_texts

        except requests.exceptions.RequestException as e:
            print(f"An error occurred during the API request: {e}")
            # You can inspect the response text for more specific API errors
            if 'response' in locals() and hasattr(response, 'text'):
                print(f"API Response Body: {response.text}")
            return None
        except KeyError:
            print("Error: Could not parse 'reviews' from the API response.")
            return None 
        
if __name__ == "__main__":
    amenitydatasource = ReviewsDataSource()
    
    place_id = amenitydatasource.get_place_id("Shri Sai Darshan Sector 4 Airoli Navi Mumbai")
    reviewList = amenitydatasource.get_reviews_by_place_id(place_id)
    
    print(reviewList)
