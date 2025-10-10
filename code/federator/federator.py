import json
from typing import Dict, Any, Union
from pathlib import Path
from data_connector import SQLConnector
from sql_wrapper import SQLWrapper
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

    def load_from_json_file(self, json_path: Union[str, Path]):
        """
        Read a JSON file and create SubQuery objects.
        Handles both list and dictionary types for 'keyword'.
        """
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

    # -----------------------------
    # Future extensibility points
    # -----------------------------

    # inside FederationManager

    def flats_query_execute(self, subquery):
        print(f"\n[Executing] {subquery.name} for city {subquery.city}")

        wrapper = SQLWrapper("../schema_mapping.json")
        translated_query = wrapper.prepare_query(subquery)

        # You can later route to remote DBs using city mappings
        db_config = {
            "host": os.getenv("host"),
            "user": os.getenv("root"),
            "password": os.getenv("password"),
            "database": os.getenv("database")
        }

        connector = SQLConnector(**db_config)
        raw_result = connector.execute_query(translated_query)

        if raw_result:
            mapped_result = wrapper.map_to_global_schema(raw_result, subquery.city)
            subquery.result = mapped_result
            print(f"→ Retrieved {len(mapped_result)} rows (normalized).")
        else:
            print("No data returned.")
            
        return subquery.result
        

    def amenities_query_execute(self,subquery,flats_data):
        pass

    def review_query_execute(self,subquery,flats_data):
        pass

    def execute_subquery(self,subquery,type,extra=None):
        
        if type == "flats":
            return self.flats_query_execute(subquery)            
        elif type == "amenities":
            return self.amenities_query_execute(subquery,extra)
        else:
            return self.review_query_execute(subquery,extra)
            
    def integrate_results(self,flats_data,amenities_datam,reviews_data):
        pass
        """
        Placeholder for combining data from multiple sources.
        """
        print("[TODO] Integrate results from all subqueries.")

    # -----------------------------
    # Pipeline runner
    # -----------------------------
    def run(self, json_path: Union[str, Path]):
        """
        Runs the federation pipeline:
        1. Load subqueries from JSON
        2. List them for verification
        3. (Future) Connect to data sources
        4. (Future) Execute subqueries
        5. (Future) Integrate results
        """
        print(f"Running Federation Pipeline for: {json_path}")
        self.load_from_json_file(json_path)
        self.list_subqueries()

        # print("\n--- Federation Steps (to be implemented) ---")
        for subquery in self.subqueries.values():
            if subquery.name == "flats_used":
                flats_data = self.execute_subquery(subquery,"flats")
                print(flats_data)
                break
            
        for subquery in self.subqueries.values():
            if subquery.name == "amenities":
                amenities_data = self.execute_subquery(subquery,"amenities",flats_data)
                print(amenities_data)
            elif subquery.name == "reviews":
                review_data = self.execute_subquery(subquery,"reviews",flats_data)
                print(review_data)
                
        final_result = self.integrate_results(flats_data,amenities_data,review_data)
        print(final_result)
        
        return final_result
    
    
# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    federation = FederationManager()
    federation.run("../query_input.json")

