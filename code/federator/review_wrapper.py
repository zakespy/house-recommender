import json # <--- Import the json library
from datasources.datasource3_reviews.reviews import ReviewsDataSource

class ReviewsWrapper:
    
    def __init__(self, config_path):
        
        config = self._load_schema_config(config_path)
        self.global_schema = config["global_schema"]
        self.city_schemas = config["city_schemas"]

    def _load_schema_config(self, path):
        """A helper method to load and parse the JSON configuration file."""
        print(f"[SQLWrapper] Loading schema configuration from: {path}")
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise ValueError(f"Configuration file not found at '{path}'")
        except json.JSONDecodeError:
            raise ValueError(f"Error decoding JSON from the configuration file '{path}'")
    # ---------------------------------------------------------------------
    
    def prepare_query(self, subquery):
       pass

    # ---------------------------------------------------------------------
    def map_to_global_schema(self, sql_result, city):
       pass 
   
    # ---------------------------------------------------------------------
    def review_query_execute(self, subquery, flats_data):
        """
        For each flat (row), call the Google Text Search API for each amenity.
        Input:
            subquery.reviews → list of reviews (strings)
            flats_data → list of dicts (rows from SQL)
        Output:
            list of dicts with building info and amenity counts
        """
        print(f"[reviewsWrapper] Running reviews query for {len(flats_data)} flats...")

        data_source = ReviewsDataSource()
        # reviews_list = subquery.reviews
        results = []
        for row in flats_data:
            reviewList = []
            bldg_name = row.get("bldg_name", "")
            loc1 = row.get("preferred_location", "")
            loc2 = row.get("preferred_location2", "")  # optional
            address = " ".join([bldg_name, loc1, loc2]).strip()
            row_result = {
                "bldg_name": bldg_name,
                "preferred_location": loc1,
                "preferred_location2": loc2,
            }
            
            place_id = data_source.get_place_id(address)
            reviewList = data_source.get_reviews_by_place_id(place_id)
                
            

            # For each amenity, get count using Google API
            

        # print(f"[reviewsWrapper] Completed reviews search for {len(results)} entries.")
        return results
         