import json
import re

class SQLWrapper:
    """
    Wrapper for SQL data sources.
    - Translates global queries into city-specific schema queries.
    - Maps local query results into global schema format.
    """
    def __init__(self, config_path):
        
        # NOTE: In a real application, config_path would point to a JSON file.
        # For this example, we assume this file is loaded correctly by the environment.
        config = self._load_schema_config(config_path)
        self.global_schema = config["global_schema"]
        self.city_schemas = config["city_schemas"]

    def _load_schema_config(self, path):
        """A helper method to load and parse the JSON configuration file."""
        print(f"[SQLWrapper] Loading schema configuration from: {path}")
        # Placeholder for actual file loading in a sandboxed environment
        # In a real environment, you'd load the JSON file here.
        
        # Mocking the configuration for demonstration:
        if path == "dummy_config.json":
            return {
                "global_schema": ["city", "preferred_location", "budget", "bedrooms", "property_type", 
                                "furnish_type", "price", "amenities", "average_rating", "no_of_reviews", "area"],
                "city_schemas": {
                    "kolkata": {
                        "table": "kolkata_flats_table",
                        "fields": {
                            "preferred_location": {"local_name": "LOCATION_NAME", "type": "text"},
                            "preferred_location2": {"local_name": "LOCALITY_NAME", "type": "text"},
                            "city": {"local_name": "city_col", "type": "text"},
                            "budget": {"local_name": "PRICE", "type": "numeric"},
                            # ... other mappings
                        }
                    }
                }
            }
        
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
        - Translates fields, including Full-Text Search expressions.
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

        # 1. Remove City Filter (if present)
        city_pattern = r'\bAND\s+city\s*=\s*\'[^\']+\'|\bcity\s*=\s*\'[^\']+\'\s+AND'
        query = re.sub(city_pattern, "", query, flags=re.IGNORECASE)
        
        lone_city_pattern = r'WHERE\s+city\s*=\s*\'[^\']+\''
        query = re.sub(lone_city_pattern, "", query, flags=re.IGNORECASE)


        # 2. Translate Global Fields to Local Fields
        for global_field, mapping_info in fields.items():
            local_field = mapping_info.get("local_name")
            field_type = mapping_info.get("type")

            if not local_field:
                continue

            # --- Dedicated logic for Full-Text Search (MATCH AGAINST) expressions ---
            # Pattern to find 'MATCH(global_field)' anywhere in the query
            fts_pattern = rf"(MATCH\s*\()(\s*{re.escape(global_field)}\s*)(\))"
            
            # Replacement: Use the local field name inside the MATCH() function
            fts_replacement = lambda m: f"{m.group(1)}{local_field}{m.group(3)}"
            
            # Perform replacement and check if the FTS pattern was found
            if re.search(fts_pattern, query, flags=re.IGNORECASE):
                query = re.sub(fts_pattern, fts_replacement, query, flags=re.IGNORECASE)
                # After translating the MATCH part, we can skip the standard text/numeric replacement
                # for this field, as it's fully translated.
                continue
            # --- END FTS LOGIC ---

            # Standard text translation (if not handled by FTS above)
            if field_type == "text":
                pattern = rf"\b{re.escape(global_field)}\s*=\s*'([^']+)'"
                replacement = lambda m: f"{local_field} LIKE '%{m.group(1)}%'"
                query = re.sub(pattern, replacement, query, flags=re.IGNORECASE)
            
            # Standard numeric and general translation
            else:
                # Fix quoting for numeric comparisons (e.g., area <= '3100' -> area <= 3100)
                numeric_fix_pattern = rf"\b{re.escape(global_field)}\s*([<>=!]+)\s*'(\d+(\.\d+)?)'"
                numeric_fix_replacement = lambda m: f"{global_field} {m.group(1)} {m.group(2)}"
                query = re.sub(numeric_fix_pattern, numeric_fix_replacement, query, flags=re.IGNORECASE)
                
                # General replacement for all other uses (e.g., bedrooms IN (2, 3))
                pattern_general = rf'\b{re.escape(global_field)}\b'
                query = re.sub(pattern_general, local_field, query, flags=re.IGNORECASE)

        # 3. Replace Table Name
        query = re.sub(r'\bFROM\s+\w+', f'FROM {table}', query, flags=re.IGNORECASE)
        
        # 4. Map selected columns to local names with global aliases
        selected_cols_list = []
        for global_field in self.global_schema:
            mapping_info = fields.get(global_field)
            if mapping_info and mapping_info.get("local_name"):
                local_field = mapping_info["local_name"]
                # FIX: Switched to using a single space delimiter instead of newline/tabs 
                # to prevent MySQL syntax error due to client parsing issues.
                selected_cols_list.append(f'{local_field} AS `{global_field}`')

        # Change: Join columns with ", " instead of ",\n    "
        selected_cols = ", ".join(selected_cols_list)
        # Change: Substitute SELECT * with SELECT {columns} on a single line
        query = re.sub(r'SELECT\s+\*', f'SELECT {selected_cols}', query, flags=re.IGNORECASE)

        print(f"\n[SQLWrapper] Translated query for {city}:\n{query}")
        return query
    
    # ---------------------------------------------------------------------
    def map_to_global_schema(self, sql_result, city):
        """
        Convert local table result rows into the global schema structure.
        
        NOTE: This is largely covered by the 'AS' aliases in prepare_query.
        """
        schema_info = self.city_schemas.get(city)
        if not schema_info:
            raise ValueError(f"No schema mapping found for city '{city}'")

        # Since prepare_query uses 'AS "global_field"', the database should return results 
        # with global field names, making a complex re-mapping unnecessary here.
        # This function would mainly be used if the database client returned raw column names.
        
        # For simplicity, we just return the result assuming the 'AS' aliases worked.
        return sql_result