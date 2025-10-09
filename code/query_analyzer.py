import json
from llm_inference import inference

USER_PROMPT = """
You are real estate expert. Giving following user query, find out the necessary details such as city, location where user wants flat, how many children it have, do it have parents.
Extract these details from the given user prompt in following dictionary output:
city: (you have to select from mumbai, hyderabad, kolkata and gurgaon)
location_preference: (if mentioned)
work_location: (if mentioned)
have_children: (if mentioned)
have_parent: (if mentioned)
budget: (if mentioned)

Following is an example:
Example USER_PROMPT: I want a flat in Mira Road, Mumbai. My job location is Office No.H/111-113, Poonam Shrusti, Opp.S.K. Stone Police Chawky, Mira Bhayandar Road, Poonam Garden Rd, Chandan Shanti, Mira Road East, Mira Bhayandar, Maharashtra 401107. I have 2 children and mother and father. So, suggest me some flats near by.
Example Preferred output:
"city": "mumbai",
"location_preference": "Mira Road, Mumbai",
"work_location": "Office No.H/111-113, Poonam Shrusti, Opp.S.K. Stone Police Chawky, Mira Bhayandar Road, Poonam Garden Rd, Chandan Shanti, Mira Road East, Mira Bhayandar, Maharashtra 401107",
"have_children": true,
"have_parent": true

Find the essential details for following user prompt as mentioned in above example.
USER_PROMPT: {user_prompt}
"""

class query_analyzer():
    def __init__(self):
        pass

    def analyze(self, user_prompt):
        response = inference(USER_PROMPT.replace('{user_prompt}', user_prompt))
        result = json.loads(response)
        return result

# user_query = """I'm looking for a 2 or 3 BHK flat in Thane, preferably close to my office at Office No. 214, Sunrise Business Park, Wagle Estate, Thane West, Mumbai, Maharashtra 400604. The flat should be in a safe and peaceful locality, as I’ll be living with my parents and two children. Please suggest nearby residential societies or housing projects that offer good connectivity, schools, markets, and hospitals within a short distance."""
# user_details = inference(USER_PROMPT.replace('{user_prompt}', user_query))
# data = json.loads(user_details)

# print(data)