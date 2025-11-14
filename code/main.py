import sys
import os

# --- Add these lines to the top of your file ---
# This finds the project's root directory (which is one level up from 'code')
# and adds it to the list of places Python looks for modules.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)


import query_analyzer as qa
import query_decomposer as qd
from federator.federator import FederationManager
from llm_inference import inference

import json

final_result_prompt = """
You are a smart real estate summarization agent. 
You take structured data (in dictionary format) about properties and generate short, human-readable summaries that compare flats by amenities, price, and value for money.

Sort and present the flats in descending order of overall value for money (best first).

For each flat:
- Write a short 2–3 sentence summary describing its key details (price, area, bedrooms, amenities, and highlights).
- Emphasize what makes it stand out (e.g., best value, premium quality, or affordable choice).
- Do NOT include explicit “Rank 1 / Rank 2 / Rank 3” text — only order them accordingly but you can give very small 20-30 word reasoning for that ranking.
- Use a natural, conversational tone suitable for a property recommendation.

Here is the property data:
{federated_result}

"""

example_prompt = """I am looking for a 2 or 3 BHK, approximately 2200 sqft, not furnished flat for rent in Gurgaon. My preferred locality is Sector 104 Gurgaon, as it needs to be close to my office at Google Signature Towers, NH 8, Sector 15, Gurugram, Haryana 122001."""
# example_prompt = """I'm looking for a 2 or 3 BHK 3000 sqft fully furnished flat in Navi mumbai, preferably close to my office at Office No. 214, Sunrise Business Park, Wagle Estate, Navi Mumbai, Mumbai, Maharashtra 400604. The flat should be in a safe and peaceful locality, as I’ll be living with my parents and two children. Please suggest nearby residential societies or housing projects that offer good connectivity, schools, markets, and hospitals within a short distance."""

def run(input_prompt: str = example_prompt):
    keywords = qa.query_analyzer().analyze(user_prompt=input_prompt)
    print("--- Extracted Keywords ---")
    print(keywords)

    decomposed_queries = qd.query_decomposer().decompose(keywords)
    print("--- Decomposed Queries ---")
    print(json.dumps(decomposed_queries, indent=4))
    
    print("--- Running Federation Pipeline ---")
    federation = FederationManager()
    federated_result = federation.run(json_data=decomposed_queries)

    print("--- Final Summarized Results ---")
    result = inference(user_prompt=final_result_prompt.format(federated_result=json.dumps(federated_result)))
    print(result)

    return result





if __name__ == "__main__":
    run()