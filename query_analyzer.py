from openai import OpenAI
import json
from dotenv import load_dotenv, find_dotenv, get_key

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

def inference(user_prompt):
    client = OpenAI(
        base_url = "https://integrate.api.nvidia.com/v1",
        api_key = get_key(find_dotenv(), "NVIDIA_API_KEY")
    )

    completion = client.chat.completions.create(
        model="qwen/qwen3-next-80b-a3b-instruct",
        messages=[{"role":"user","content":USER_PROMPT.format(user_prompt=user_prompt)}],
        temperature=0.2,
        top_p=0.7,
        max_tokens=8192,
        stream=False
    )

    # for chunk in completion:
    #     reasoning = getattr(chunk.choices[0].delta, "reasoning_content", None)
    #     if reasoning:
    #         print(reasoning, end="")
    #     if chunk.choices[0].delta.content is not None:
    #         print(chunk.choices[0].delta.content, end="")

    return completion.choices[0].message.content.strip('\n')


user_prompt = """I'm looking for a 2 or 3 BHK flat in Thane, preferably close to my office at Office No. 214, Sunrise Business Park, Wagle Estate, Thane West, Mumbai, Maharashtra 400604. The flat should be in a safe and peaceful locality, as I’ll be living with my parents and two children. Please suggest nearby residential societies or housing projects that offer good connectivity, schools, markets, and hospitals within a short distance."""
user_details = inference(user_prompt)
data = json.loads(user_details)

print(data)