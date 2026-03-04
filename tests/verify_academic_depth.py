import os
import sys

# Ensure project root is in path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.controller import handle_question

def verify_response_quality(query: str):
    print(f"\n[Verification] Query: {query}")
    result = handle_question(query)
    answer = result['answer']
    
    print("\n[Raw Response]")
    print(answer)
    print("\n[Response Overview]")
    print(f"Total length: {len(answer)} characters")
    
    paragraphs = [p.strip() for p in answer.split('\n\n') if p.strip()]
    print(f"Total paragraphs: {len(paragraphs)}")
    
    # Check sections (1 to 9)
    sections_found = []
    for i, seq_name in enumerate(sections_req):
        num_header = f"{i+1}."
        if num_header in answer or seq_name.lower() in answer.lower():
            sections_found.append(seq_name)
    
    print(f"Sections found: {len(sections_found)}/{len(sections_req)}")
    
    if len(sections_found) == len(sections_req):
        print("\n[SUCCESS] Response meets structure requirements.")
    else:
        print("\n[PARTIAL] Response does not fully meet structure requirements.")

if __name__ == "__main__":
    # Test with a question likely to have articles
    verify_response_quality("Why did Jesus ask Peter if he loved him three times?")
