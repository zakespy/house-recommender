import json # <--- Import the json library
from datasources.datasource2_amenities.amenities import AmenitiesDataSource

class AmenitiesWrapper:
    
    def __init__(self, config_path):
       
        self.city_schemas = self._load_schema_config(config_path)

       
        self.global_schema = [
        "city",
        "city_area",
        "preferred_location",
        "budget",
        "bedrooms",
        "coordinate",
        "furnish_type",
        "area",
        "bldg_name",
        "price",
        "amenities",
        "average_rating",
        "no_of_reviews"
      ]

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
        """
        Adjust the SQL query for the city-specific schema.
        """
        city = subquery.city
        schema_info = self.city_schemas.get(city)

        if not schema_info:
            raise ValueError(f"No schema mapping found for city '{city}'")

        table = schema_info["table"]
        fields = schema_info["fields"]

        
        if subquery.query:
           
            selected_cols_list = []
            for global_field in self.global_schema:
                local_field = fields.get(global_field)
                if local_field:
                    
                    selected_cols_list.append(f'{local_field} AS "{global_field}"')

            selected_cols = ", ".join(selected_cols_list)
            adjusted_query = f"SELECT {selected_cols} FROM {table}"
            print(f"[SQLWrapper] Translated query for {city}: {adjusted_query}")
            return adjusted_query
        else:
            raise ValueError(f"No query found in subquery '{subquery.name}'")

    # ---------------------------------------------------------------------
    def map_to_global_schema(self, sql_result, city):
        """
        Convert local table result rows into the global schema structure.
        
        NOTE: If you use the improved 'prepare_query' method with 'AS' aliases,
        this mapping function becomes much simpler or even unnecessary, as the
        database already returns the data with the correct global field names.
        """
        schema_info = self.city_schemas.get(city)
        if not schema_info:
            raise ValueError(f"No schema mapping found for city '{city}'")

        reverse_map = {v: k for k, v in schema_info["fields"].items()}

        mapped_data = []
        for row in sql_result:
            mapped = {}
            for local_field, value in row.items():
                global_field = reverse_map.get(local_field)
                if global_field:
                    mapped[global_field] = value
            mapped_data.append(mapped)

        return mapped_data
   
    # ---------------------------------------------------------------------
    def amenities_query_execute(self, subquery,extra):
        pass
     
         