import json
from llm_inference import inference

USER_PROMPT = """
You are real estate expert. Giving following user query, find out the necessary details such as city, location where user wants flat, how many children it have, do it have parents.
Extract these details from the given user prompt in following dictionary output:
city: (you have to select from mumbai, hyderabad, kolkata and gurgaon)
location_preference:
work_location:
no_of_children:
have_parent:

Following is an example:
Example USER_PROMPT: I want a flat in Mira Road, Mumbai. My job location is Office No.H/111-113, Poonam Shrusti, Opp.S.K. Stone Police Chawky, Mira Bhayandar Road, Poonam Garden Rd, Chandan Shanti, Mira Road East, Mira Bhayandar, Maharashtra 401107. I have 2 children and mother and father. So, suggest me some flats near by.
Example Preferred output:
"city": "mumbai",
"location_preference": "Mira Road, Mumbai",
"work_location": "Office No.H/111-113, Poonam Shrusti, Opp.S.K. Stone Police Chawky, Mira Bhayandar Road, Poonam Garden Rd, Chandan Shanti, Mira Road East, Mira Bhayandar, Maharashtra 401107",
"no_of_children": 2,
"have_parent": true

Find the essential details for following user prompt as mentioned in above example.
USER_PROMPT: {user_prompt}
"""




user_prompt = """I'm looking for a 2 or 3 BHK flat in Thane, preferably close to my office at Office No. 214, Sunrise Business Park, Wagle Estate, Thane West, Mumbai, Maharashtra 400604. The flat should be in a safe and peaceful locality, as I’ll be living with my parents and two children. Please suggest nearby residential societies or housing projects that offer good connectivity, schools, markets, and hospitals within a short distance."""
user_details = inference(USER_PROMPT.replace('{user_prompt}', user_prompt))
data = json.loads(user_details)

print(data)