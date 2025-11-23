import json
import re

class query_decomposer:
    def __init__(self):
        self.global_schema_columns = [
            "city", "preferred_location", "budget", "bedrooms", "property_type", 
            "furnish_type", "price", "amenities", "average_rating", "no_of_reviews", "area"
        ]

    def decompose(self, keywords):
        """
        Takes structured keywords and generates SQL queries for different logical components.
        """
        city = keywords.get("city", None)
        
        # --- Location Preference 1 Processing ---
        location_preference = keywords.get("location_preference", None)
        location_preference = re.sub(r'[^a-zA-Z0-9\s]+', ' ', location_preference).lower().strip() if location_preference is not None else None
        print("location preference  ",location_preference)
        
        # --- Location Preference 2 Processing ---
        location_preference2 = keywords.get("location_preference2", None)
        # Cleaning the keyword for use in the full-text search query
        location_preference2 = re.sub(r'[^a-zA-Z0-9\s]+', ' ', location_preference2).lower().strip() if location_preference2 is not None else None
        print("location preference 2 ",location_preference2)
        
        area = keywords.get("area", None)
        
        budget = keywords.get("budget", None)
        budget = budget * 1.1 if budget is not None else 0

        bedrooms = keywords.get("bedrooms", None)
        bedrooms = tuple(bedrooms) if bedrooms is not None else 0
        if bedrooms != 0:
            # Ensure bedrooms is formatted correctly for SQL IN clause
            bedrooms = f"({bedrooms[0]})" if len(bedrooms) == 1 else bedrooms
        else:
            bedrooms = 0
        
        have_children = keywords.get("have_children", None)
        have_parent = keywords.get("have_parent", None)
        furnished = keywords.get("furnish_type", None)

        # --- Base Query Construction ---
        base_query = "SELECT * FROM flats_data WHERE"
        
        # Filter 1: City
        if city:
            base_query += f" city = '{city}'"
        
        # Filter 2: Preferred Location 1 (Assuming a standard '=' match for now)
        if location_preference:
            # Note: For 'preferred_location', you might want to use MATCH() AGAINST() here too 
            # if 'preferred_location' is also a full-text indexed column.
            base_query += f" AND MATCH(preferred_location) AGAINST('{location_preference}\' IN BOOLEAN MODE)"
        
        # Filter 3: Preferred Location 2 - Using Full-Text Search (MATCH AGAINST)
        # This assumes the column in flats_data is named 'preferred_location2'
        if location_preference2:
            # Using the exact phrase search ("...") in BOOLEAN MODE
            # We assume a FULLTEXT index exists on the 'preferred_location2' column
            base_query += f" AND MATCH(preferred_location2) AGAINST('\"{location_preference2}\"' IN BOOLEAN MODE)"
        
        # Filter 4: Area
        if area:
            base_query += f" AND area <= {area} + 100 AND area >= {area} - 100"
        
        # Filter 5: Budget
        if budget:
            base_query += f" AND price <= {budget}"
        
        # Filter 6: Bedrooms
        if bedrooms:
            base_query += f" AND bedrooms IN {bedrooms}"
        
        # Filter 7: Furnish Type
        if furnished:
            base_query += f" AND furnish_type = {furnished}"
        
        base_query += " LIMIT 10;"
        
        # --- Amenities Query (Unchanged) ---
        amenities_query = {
            "city": city,
            "area": area,
            "amenities": ["hospital","Gym", "Swimming Pool", "Club House"] 
        }
        if (have_children):
            amenities_query["amenities"].extend(["Children's Play Area", "School Nearby"])
        if (have_parent):
            amenities_query["amenities"].extend(["nursery", "Park Nearby"])
        
        # --- Review Query (Unchanged) ---
        review_query = {
            "city": city,
            "area": area,
            "reviews_source": "google_maps",
            "fields": ["average_rating", "review_summary", "no_of_reviews"]
        }

        # --- Final Decomposed Structure ---
        decomposed_query = {
            "flats_data": {
                "query": base_query,
                "keywords_used": list(keywords.keys()),
                "city": city
            },
            "amenities_data": amenities_query,
            "reviews_data": review_query
        }

        return decomposed_query


# ------------------- Example Usage -------------------
if __name__ == "__main__":
    global_schema_columns = [
        "city", "preferred_location", "budget", "bedrooms", "property_type", 
        "furnish_type", "price", "amenities", "average_rating", "no_of_reviews"
    ]

    # Example Input Data
    analyzer_output = {
        'city': 'mumbai', 
        'location_preference': 'Thane', 
        'location_preference2': 'sector 5 salt lake', # This is now the Full-Text Search target
        'work_location': 'Office No. 214, Sunrise Business Park, Wagle Estate, Thane West, Mumbai, Maharashtra 400604', 
        'have_children': True, 
        'have_parent': True, 
        'furnish_type': 1, 
        'budget': 50000, 
        'bedrooms': [2, 3], 
        'area': 3000
    }

    decomposer = query_decomposer()
    output = decomposer.decompose(analyzer_output)

    print(json.dumps(output, indent=4))
    print("\n--- Generated SQL Query (flats_data) ---")
    print(output['flats_data']['query'])