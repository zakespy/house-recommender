import json # <--- Import the json library
from datasources.datasource2_amenities.amenities import AmenitiesDataSource

class AmenitiesWrapper:
        
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
        # """
        # Convert local table result rows into the global schema structure.
        
        # NOTE: If you use the improved 'prepare_query' method with 'AS' aliases,
        # this mapping function becomes much simpler or even unnecessary, as the
        # database already returns the data with the correct global field names.
        
        # """
        pass 
        
    # ---------------------------------------------------------------------
    # def amenities_query_execute(self, subquery,extra):
    #     pass


    def amenities_query_execute(self, subquery, flats_data):
        """
        For each flat (row), call the Google Text Search API for each amenity.
        Input:
            subquery.amenities → list of amenities (strings)
            flats_data → list of dicts (rows from SQL)
        Output:
            list of dicts with building info and amenity counts
        """
        # print(f"[AmenitiesWrapper] Running amenities query for {len(flats_data)} flats...")

        data_source = AmenitiesDataSource()
        amenities_list = subquery.amenities
        results = []
        
        if( flats_data is None or len(flats_data) == 0):
            print("got empty flats data in amenitites wrapper")
        

        for row in flats_data:
            bldg_name = row.get("bldg_name", "")
            loc1 = row.get("preferred_location", "")
            loc2 = row.get("preferred_location2", "") 
            parts = [str(x) if x else "" for x in [bldg_name, loc1, loc2]]
            address = " ".join(parts).strip()

            print("done with address prep")
            row_result = {
                "bldg_name": bldg_name,
                "preferred_location": loc1,
                "preferred_location2": loc2,
            }

            # For each amenity, get count using Google API
            for amenity in amenities_list:
                try:
                    count = data_source.textsearch_api(amenity, address)
                    row_result[amenity] = count
                except Exception as e:
                    print(f"[Warning] Amenity '{amenity}' failed for {address}: {e}")
                    row_result[amenity] = 0

            results.append(row_result)

        # print(f"[AmenitiesWrapper] Completed amenities search for {len(results)} entries.")
        return results
        