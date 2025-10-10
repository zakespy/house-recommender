import json # <--- Import the json library
import re

class SQLWrapper:
    """
    Wrapper for SQL data sources.
    - Translates global queries into city-specific schema queries.
    - Maps local query results into global schema format.
    """
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
        """
        Convert global SQL query into city-specific SQL query.
        - Removes redundant city filter.
        - Translates other fields, using LIKE for text.
        """
        city = subquery.city
        schema_info = self.city_schemas.get(city)
        if not schema_info:
            raise ValueError(f"No schema mapping found for city '{city}'")

        table = schema_info["table"]
        fields = schema_info["fields"]

        if not subquery.query:
            raise ValueError(f"No query found in subquery '{getattr(subquery, 'name', 'unknown')}'")

        query = subquery.query.strip()

       
        city_pattern = r'\bAND\s+city\s*=\s*\'[^\']+\'|\bcity\s*=\s*\'[^\']+\'\s+AND'
        query = re.sub(city_pattern, "", query, flags=re.IGNORECASE)
       
        lone_city_pattern = r'WHERE\s+city\s*=\s*\'[^\']+\''
        query = re.sub(lone_city_pattern, "", query, flags=re.IGNORECASE)


        for global_field, mapping_info in fields.items():
            # This logic remains the same as before...
            local_field = mapping_info.get("local_name")
            field_type = mapping_info.get("type")

            if not local_field:
                continue

            if field_type == "text":
                pattern = rf"\b{re.escape(global_field)}\s*=\s*'([^']+)'"
                replacement = lambda m: f"{local_field} LIKE '%{m.group(1)}%'"
                query = re.sub(pattern, replacement, query, flags=re.IGNORECASE)
            else:
                
                numeric_fix_pattern = rf"\b{re.escape(global_field)}\s*([<>=!]+)\s*'(\d+(\.\d+)?)'"
               
                numeric_fix_replacement = lambda m: f"{global_field} {m.group(1)} {m.group(2)}"
                query = re.sub(numeric_fix_pattern, numeric_fix_replacement, query, flags=re.IGNORECASE)

                
                pattern_general = rf'\b{re.escape(global_field)}\b'
                query = re.sub(pattern_general, local_field, query, flags=re.IGNORECASE)

      
        query = re.sub(r'\bFROM\s+\w+', f'FROM {table}', query, flags=re.IGNORECASE)
        
        selected_cols_list = []
        for global_field in self.global_schema:
            mapping_info = fields.get(global_field)
            if mapping_info and mapping_info.get("local_name"):
                local_field = mapping_info["local_name"]
                selected_cols_list.append(f'{local_field} AS "{global_field}"')

        selected_cols = ",\n    ".join(selected_cols_list)
        query = re.sub(r'SELECT\s+\*', f'SELECT\n    {selected_cols}', query, flags=re.IGNORECASE)

        print(f"\n[SQLWrapper] Translated query for {city}:\n{query}")
        return query
    
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