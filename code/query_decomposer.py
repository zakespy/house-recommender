import json

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
        area = keywords.get("location_preference", None)
        budget = keywords.get("budget", None)
        bedrooms = keywords.get("bedrooms", None)
        have_children = keywords.get("have_children", None)
        have_parent = keywords.get("have_parent", None)
        furnished = keywords.get("furnish_type", None)

        
        # 1️⃣ Create SQL query for main flat search
        base_query = "SELECT * FROM flats_data WHERE"
        if city:
            base_query += f" city = '{city}'"
        if area:
            base_query += f" AND preferred_location = '{area}'"
        if budget:
            base_query += f" AND price <= {budget}"
        if bedrooms:
            base_query += f" AND bedrooms = {bedrooms}"
        if furnished:
            base_query += f" AND furnish_type = {furnished}"
        
        
        # 2️⃣ Amenities and Review info – placeholders (will be handled by federator)
        amenities_query = {
            "city": city,
            "area": area,
            "amenities": ["Gym", "Swimming Pool", "Club House"]  # Example - later from API
        }
        if (have_children):
            amenities_query["amenities"].extend(["Children's Play Area", "School Nearby"])
        if (have_parent):
            amenities_query["amenities"].extend(["Hospital Nearby", "Park Nearby"])
        
        review_query = {
            "city": city,
            "area": area,
            "reviews_source": "google_maps",
            "fields": ["average_rating", "review_summary", "no_of_reviews"]
        }

        # 3️⃣ Combine into unified JSON
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
# if __name__ == "__main__":
#     global_schema_columns = [
#         "city", "preferred_location", "budget", "bedrooms", "property_type", 
#         "furnish_type", "price", "amenities", "average_rating", "no_of_reviews"
#     ]

#     analyzer_output = {
#         "city": "Thane",
#         "preferred_location": "Mira Road",
#         "budget": 3000000,
#         "bedrooms": 3
#     }

#     decomposer = query_decomposer()
#     output = decomposer.decompose(analyzer_output)

#     print(json.dumps(output, indent=4))
