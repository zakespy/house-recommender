import query_analyzer as qa
import query_decomposer as qd
import json

def run():
    prompt = """I'm looking for a 2 or 3 BHK flat in Thane, preferably close to my office at Office No. 214, Sunrise Business Park, Wagle Estate, Thane West, Mumbai, Maharashtra 400604. The flat should be in a safe and peaceful locality, as I’ll be living with my parents and two children. Please suggest nearby residential societies or housing projects that offer good connectivity, schools, markets, and hospitals within a short distance."""
    
    keywords = qa.query_analyzer().analyze(user_prompt=prompt)
    print("--- Extracted Keywords ---")
    print(keywords)

    decomposed_queries = qd.query_decomposer().decompose(keywords)
    print("--- Decomposed Queries ---")
    print(json.dumps(decomposed_queries, indent=4))




    
if __name__ == "__main__":
    run()