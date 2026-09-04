import time
import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.bible_loader import load_bible, get_passage

def test_performance():
    print("--- Bible Loader Performance Test ---")
    
    # 1. Measure initial load (parsing JSON + indexing)
    start = time.time()
    load_bible()
    load_time = (time.time() - start) * 1000
    print(f"Initial Load & Index: {load_time:.2f}ms")
    
    # 2. Measure O(1) retrieval for 2 Kings 4
    # 2 Kings is book 12
    start = time.time()
    verses = get_passage(12, 4)
    retrieval_time = (time.time() - start) * 1000
    print(f"Retrieval (2 Kings 4): {retrieval_time:.4f}ms")
    print(f"Verses found: {len(verses)}")
    
    if len(verses) > 0:
        print(f"First Verse Sample: {verses[0]['t'][:50]}...")
        
    # 3. Repeat 1000 times to show average speed
    start = time.time()
    for _ in range(1000):
        get_passage(12, 4)
    avg_time = ((time.time() - start) / 1000) * 1000
    print(f"Average Retrieval Time (1000 iterations): {avg_time:.4f}ms")

if __name__ == "__main__":
    test_performance()
