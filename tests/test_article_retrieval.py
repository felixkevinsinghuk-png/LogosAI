import os
import sys

# Ensure project root is in path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.controller import handle_question
from vector_store.vector_db import index_articles

def test_restoration_query():
    print("\n--- Testing Restoration Query (John 21) ---")
    # Ensure articles are indexed
    index_articles(force=True)
    
    question = "Why did Jesus ask Peter if he loved him three times?"
    response = handle_question(question)
    
    print(f"QUERY: {question}")
    print(f"PASSAGES RETRIEVED: {len(response['passages'])}")
    print(f"ARTICLES RETRIEVED: {len(response['articles'])}")
    
    for article in response['articles']:
        print(f" - [{article['source']}] (Score: {article['score']:.3f})")
    
    print("\n--- LLM ANSWER ---")
    print(response['answer'])
    print("------------------\n")

def test_no_articles_query():
    print("\n--- Testing No Articles Query ---")
    question = "Who was the first king of Israel?"
    response = handle_question(question)
    
    print(f"QUERY: {question}")
    print(f"ARTICLES RETRIEVED: {len(response['articles'])}")
    
    # We expect the LLM to output "No trusted contextual sources were found for this question." 
    # if no articles are found in the retrieval step.
    if not response['articles']:
        print("Success: No articles retrieved as expected.")
    
    print("\n--- LLM ANSWER ---")
    print(response['answer'])
    print("------------------\n")

if __name__ == "__main__":
    # Create tests directory if it doesn't exist
    os.makedirs(os.path.join(PROJECT_ROOT, "tests"), exist_ok=True)
    
    try:
        test_restoration_query()
        test_no_articles_query()
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
