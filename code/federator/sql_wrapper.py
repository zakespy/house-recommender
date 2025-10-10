# sql_wrapper.py
class SQLWrapper:
    """
    Wrapper for SQL data sources.
    - Translates global queries into city-specific schema queries.
    - Maps local query results into global schema format.
    """
    def __init__(self):
        # Define schema mapping for each city's table
        self.city_schemas = {
            "Mumbai": {
                "table": "mumbai",
                "fields": {
                    "flat_id": "id",
                    "city": "city_name",
                    "price": "cost",
                    "area_sqft": "size_sqft",
                    "location": "location_area",
                    "amenities": "features"
                }
            },
            "Hyderabad": {
                "table": "hyderabad",
                "fields": {
                    "flat_id": "flat_no",
                    "city": "city",
                    "price": "price_value",
                    "area_sqft": "area",
                    "location": "address",
                    "amenities": "facilities"
                }
            },
            "Kolkata": {
                "table": "kolkata",
                "fields": {
                    "flat_id": "flat_id",
                    "city": "city",
                    "price": "price",
                    "area_sqft": "sqft",
                    "location": "area_name",
                    "amenities": "amenities_list"
                }
            },
            "Gurgaon": {
                "table": "gurgaon",
                "fields": {
                    "flat_id": "flat_id",
                    "city": "city",
                    "price": "price",
                    "area_sqft": "sqft",
                    "location": "area_name",
                    "amenities": "amenities_list"
                }
            },
            
        }

        # Define your **global schema**
        self.global_schema = ["flat_id", "city", "location", "price", "area_sqft", "amenities"]

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

        # If query is generic like "SELECT * FROM flats_used"
        # replace it with city-specific table and mapped columns
        if subquery.query:
            selected_cols = ", ".join(fields.values())
            adjusted_query = f"SELECT {selected_cols} FROM {table}"
            print(f"[SQLWrapper] Translated query for {city}: {adjusted_query}")
            return adjusted_query
        else:
            raise ValueError(f"No query found in subquery '{subquery.name}'")

    # ---------------------------------------------------------------------
    def map_to_global_schema(self, sql_result, city):
        """
        Convert local table result rows into the global schema structure.
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
