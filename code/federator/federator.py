import json
from typing import Dict, Any, Union
from pathlib import Path
from federator.data_connector import SQLConnector
from federator.sql_wrapper import SQLWrapper
from federator.amenities_wrapper import AmenitiesWrapper
from federator.review_wrapper import ReviewsWrapper
from dotenv import load_dotenv
import os


class SubQuery:
    """
    Represents a single decomposed query unit.
    Each subquery can later be linked to a data source and executed independently.
    """
    def __init__(self, name: str, query: str = None, city: str = None,
                 keywords: Union[Dict[str, Any], list, None] = None, **kwargs):
        self.name = name
        self.query = query
        self.city = city
        self.keywords = keywords or {}
        self.metadata = kwargs  # any additional metadata like area, amenities, etc.
        self.result = None  # Placeholder for query result
        self.amenities = kwargs.get("amenities", [])

    def __repr__(self):
        return (f"SubQuery(name={self.name}, city={self.city}, "
                f"query={self.query}, keywords={self.keywords}), amenities={self.amenities}")


class FederationManager:
    """
    Handles loading, storing, and managing multiple subqueries.
    Future versions will handle database connections and data integration.
    """
    def __init__(self):
        self.subqueries: Dict[str, SubQuery] = {}

    def load_from_json_file(self, json_path: Union[str, Path], json_data = None):
        """
        Read a JSON file and create SubQuery objects.
        Handles both list and dictionary types for 'keyword'.
        """
        
        if json_data != None:
            data = json_data
        else:
            json_path = Path(json_path)
            if not json_path.exists():
                raise FileNotFoundError(f"JSON file not found: {json_path}")

            with open(json_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON format in {json_path}: {e}")

        for name, details in data.items():
            query = details.get("query")
            city = details.get("city")
            keywords = details.get("keyword", {})

            # Capture additional metadata like area, amenities, etc.
            extra = {k: v for k, v in details.items() if k not in ["query", "city", "keyword"]}

            self.subqueries[name] = SubQuery(
                name=name,
                query=query,
                city=city,
                keywords=keywords,
                **extra
            )

    def list_subqueries(self):
        """
        Display all loaded subqueries.
        """
        print("\n--- Loaded Subqueries ---")
        for name, subquery in self.subqueries.items():
            print(f"- {name}: {subquery}")

    def get_subquery(self, name: str) -> SubQuery:
        return self.subqueries.get(name)


    def flats_query_execute(self, subquery):
        print(f"\n[Executing] {subquery.name} for city {subquery.city}")

        wrapper = SQLWrapper("schema_mapping.json")
        translated_query = wrapper.prepare_query(subquery)

        # You can later route to remote DBs using city mappings
        # if subquery.city.lower() == "mumbai" or subquery.city.lower() == "kolkata":
        if subquery.city.lower() == "mumbai":
            print(f"→ Routing to remote database for city: {subquery.city}")
            db_config = {
                "host": os.getenv("DB_HOST"),
                "user": os.getenv("DB_USER"),
                "password": os.getenv("DB_PASSWORD"),
                "database": os.getenv("DB_NAME"),
                "port": int(os.getenv("DB_PORT", 3306))
            }
        
        else:
            print(f"Using Local System Database for city: {subquery.city}")
            db_config = {
                "host": os.getenv("DB1_HOST"),
                "user": os.getenv("DB1_USER"),
                "password": os.getenv("DB1_PASSWORD"),
                "database": os.getenv("DB1_NAME"),
                "port": int(os.getenv("DB1_PORT", 3306))
            }


        connector = SQLConnector(**db_config)
        raw_result = connector.execute_query(translated_query)

        subquery.result = raw_result
        # if raw_result:
        #     print(raw_result)
        #     mapped_result = wrapper.map_to_global_schema(raw_result, subquery.city)
        #     subquery.result = mapped_result
        #     print(f"→ Retrieved {len(mapped_result)} rows (normalized).")
        # else:
        #     print("No data returned.")
            
        return subquery.result
        

    def amenities_query_execute(self,subquery,flats_data):
        print(f"\n[Executing] Amenities query for city {subquery.city}")
        
        wrapper = AmenitiesWrapper("schema_mapping.json")

        # run amenities logic (Google search)
        result = wrapper.amenities_query_execute(subquery, flats_data)

        if result:
            print(f"→ Retrieved amenities count for {len(result)} buildings.")
        else:
            print("No amenities data returned.")

        subquery.result = result
        return result

    def review_query_execute(self,subquery,flats_data):

        wrapper = ReviewsWrapper("schema_mapping.json")

        result = wrapper.review_query_execute(subquery,flats_data)
        subquery.result = result
        return result

    def execute_subquery(self,subquery,type,extra=None):
        
        if type == "flats":
            return self.flats_query_execute(subquery)            
        elif type == "amenities":
            return self.amenities_query_execute(subquery,extra)
        else:
            return self.review_query_execute(subquery,extra)
            
    def integrate_results(self, flats_data, amenities_data, reviews_data):
        """
        Integrates results from flats, amenities, and reviews data sources.
        All inputs are list[dict], having the same number of rows and aligned order.
        Duplicate columns are merged intelligently to avoid repetition.
        """
        if not flats_data and not amenities_data and not reviews_data:
            print("[Warning] One or more datasets are empty. Integration skipped.")
            return []

        # Ensure all datasets have equal length
        n = len(flats_data)
        if len(amenities_data) != n or len(reviews_data) != n:
            raise ValueError("[Error] Datasets have mismatched lengths and cannot be merged row-wise.")

        merged_results = []
        for i in range(n):
            merged_row = {}
            for source in (flats_data[i], amenities_data[i], reviews_data[i]):
                for key, value in source.items():
                    # Keep only the first occurrence of a duplicate key
                    if key not in merged_row:
                        merged_row[key] = value
                    # Optional: handle duplicate keys differently if needed
                    # else:
                    #     merged_row[f"{key}_dup"] = value
            merged_results.append(merged_row)

        print(f"[Info] Integrated {n} records from flats, amenities, and reviews.")
        return merged_results


    
    def run(self, json_path: Union[str, Path] = None,json_data = None ):
        """
        Runs the federation pipeline:
        1. Load subqueries from JSON
        2. List them for verification
        3. (Future) Connect to data sources
        4. (Future) Execute subqueries
        5. (Future) Integrate results
        """
        print(f"Running Federation Pipeline for: {json_path}")
        self.load_from_json_file(json_path,json_data)
        self.list_subqueries()

        for subquery in self.subqueries.values():
            if subquery.name == "flats_data":
                # print("---- Executing flats query ----")
                flats_data = self.execute_subquery(subquery,"flats")
                # print(flats_data)
                print(f"Flats Data Retrieved: {len(flats_data) if flats_data is not None else 0} records")
                
        if flats_data is not None:
            for subquery in self.subqueries.values():
                # print("inside amenities loop")
                if subquery.name == "amenities_data":
                    amenities_data = self.execute_subquery(subquery,"amenities",flats_data)
                    # print(amenities_data)
                elif subquery.name == "reviews_data":
                    # print("inside reviews loop")
                    review_data = self.execute_subquery(subquery,"reviews",flats_data)
                    # print(review_data)
                
            final_result = self.integrate_results(flats_data,amenities_data,review_data)
            print(final_result)
            
            return final_result
        
        return {"message": "No flats data retrieved, skipping further processing."}
    
    

if __name__ == "__main__":
    
    json_string = """
    {
        "flats_data": {
            "query": "SELECT * FROM flats_data WHERE city = 'mumbai' AND preferred_location = 'Thane' AND furnish_type = 1",
            "keywords_used": [
                "city",
                "location_preference",
                "work_location",
                "have_children",
                "have_parent",
                "furnish_type",
                "budget",
                "area"
            ],
            "city": "mumbai"
        },
        "amenities_data": {
            "city": "mumbai",
            "area": "Thane",
            "amenities": [
                "Gym",
                "Swimming Pool",
                "Club House",
                "Children's Play Area",
                "School Nearby",
                "Hospital Nearby",
                "Park Nearby"
            ]
        },
        "reviews_data": {
            "city": "mumbai",
            "area": "Thane",
            "reviews_source": "google_maps",
            "fields": [
                "average_rating",
                "review_summary",
                "no_of_reviews"
            ]
        }
    }
    """

    
    federation = FederationManager()
    federation.run(json_data = json.loads(json_string))

