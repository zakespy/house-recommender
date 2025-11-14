import json # <--- Import the json library
from datasources.datasource3_reviews.reviews import ReviewsDataSource
from llm_inference import inference

REVIEW_PROMPT = """
You are real estate expert. Your task is to analyze a list of reviews for a building and provide insights on the following aspects in the following json format:
Input: List of reviews 
Output: {
    "summarize": "A brief summary of overally reviews",
    "sentiment": "Return sentiment as Positive (1), neutral (0), or negative (-1)"
    }

Based on above instructions, analyze the following reviews and ensure to return in json format:
{reviews}
"""

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
            parts = [str(x) if x else "" for x in [bldg_name, loc1, loc2]]
            address = " ".join(parts).strip()
            # address = " ".join([bldg_name, loc1, loc2]).strip()
            
            
            row_result = {
                "bldg_name": bldg_name,
                "preferred_location": loc1,
                "preferred_location2": loc2,
                "summary":None,
                "sentiment":None
            }
            
            place_id = data_source.get_place_id(address)
            reviewList = data_source.get_reviews_by_place_id(place_id)
            
            llm_analysis = inference(REVIEW_PROMPT.replace("reviews", str(reviewList)))
            llm_analysis = json.loads(llm_analysis)
            # print(llm_analysis)
            # row_result["sentiment_analysis"] = llm_analysis.get("sentiment")
            row_result["summary"] = llm_analysis.get("summarize")
            row_result["sentiment"] = llm_analysis.get("sentiment")
            results.append(row_result)
            # For each amenity, get count using Google API
            

        # print(f"[reviewsWrapper] Completed reviews search for {len(results)} entries.")
        return results
         