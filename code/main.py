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

import json

def run():
    prompt = """I am looking for a 2 or 3 BHK, approximately 2200 sqft, not furnished flat for rent in Gurgaon. My preferred locality is Sector 104 Gurgaon, as it needs to be close to my office at Google Signature Towers, NH 8, Sector 15, Gurugram, Haryana 122001."""
    # prompt1 = """I'm looking for a 2 or 3 BHK 3000 sqft fully furnished flat in Navi mumbai, preferably close to my office at Office No. 214, Sunrise Business Park, Wagle Estate, Navi Mumbai, Mumbai, Maharashtra 400604. The flat should be in a safe and peaceful locality, as I’ll be living with my parents and two children. Please suggest nearby residential societies or housing projects that offer good connectivity, schools, markets, and hospitals within a short distance."""
    keywords = qa.query_analyzer().analyze(user_prompt=prompt)
    print("--- Extracted Keywords ---")
    print(keywords)

    decomposed_queries = qd.query_decomposer().decompose(keywords)
    print("--- Decomposed Queries ---")
    print(json.dumps(decomposed_queries, indent=4))
    
    print("--- Running Federation Pipeline ---")
    federation = FederationManager()
    federation.run(json_data=decomposed_queries)





if __name__ == "__main__":
    run()