import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.bible_loader import load_bible, get_passage, BOOK_NAME_TO_NUM, BOOK_NAMES

def debug_judges():
    print("--- Debugging Judges 5 ---")
    load_bible()
    
    print(f"Judges in BOOK_NAME_TO_NUM: {'judges' in BOOK_NAME_TO_NUM}")
    book_num = BOOK_NAME_TO_NUM.get('judges')
    print(f"Book number for 'judges': {book_num}")
    
    if book_num:
        verses = get_passage(book_num, 5)
        print(f"Verses for Judges 5: {len(verses)}")
        if verses:
            print(f"First verse: {verses[0]['t'][:50]}...")
        else:
            print("No verses found for Judges 5.")
            
            # Check what chapters ARE available for Judges
            all_verses = load_bible()
            judges_verses = [v for v in all_verses if v['b'] == book_num]
            chapters = sorted(list(set([v['c'] for v in judges_verses])))
            print(f"Chapters available for Judges: {chapters}")
    else:
        print("Judges not found in book mapping.")

if __name__ == "__main__":
    debug_judges()
