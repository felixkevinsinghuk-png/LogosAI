from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import date
from backend.core.supabase_client import supabase_admin
from database.bible_loader import get_bible_path
import json
import os
from backend.core.security import get_current_user

router = APIRouter(prefix="/api/bible", tags=["bible"])

class VerseResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    error: Optional[Dict[str, Any]] = None

# Fallback verses for deterministic rotation
FALLBACK_VERSES = [
    {"text": "\"casting all your anxieties on him, because he cares for you.\"", "ref": "— 1 Peter 5:7 (ESV)", "theme": "Peace"},
    {"text": "\"For God so loved the world, that he gave his only Son, that whoever believes in him should not perish but have eternal life.\"", "ref": "— John 3:16 (ESV)", "theme": "Love"},
    {"text": "\"I can do all things through him who strengthens me.\"", "ref": "— Philippians 4:13 (ESV)", "theme": "Strength"},
    {"text": "\"Trust in the LORD with all your heart, and do not lean on your own understanding.\"", "ref": "— Proverbs 3:5 (ESV)", "theme": "Trust"},
    {"text": "\"The LORD is my shepherd; I shall not want.\"", "ref": "— Psalm 23:1 (ESV)", "theme": "Provision"},
    {"text": "\"Be strong and courageous. Do not be frightened, for the LORD your God is with you.\"", "ref": "— Joshua 1:9 (ESV)", "theme": "Courage"},
    {"text": "\"And we know that for those who love God all things work together for good.\"", "ref": "— Romans 8:28 (ESV)", "theme": "Hope"},
]

@router.get("/votd", response_model=VerseResponse)
async def get_verse_of_the_day(lang: str = Query("en")):
    """
    Returns the Verse of the Day. Tries to fetch from the database first.
    If not found, deterministically selects a verse based on the current date
    and saves it to the database to ensure all users see the same verse today.
    """
    today = date.today()
    
    # Attempt to fetch from Supabase `daily_verses`
    if supabase_admin:
        try:
            res = supabase_admin.table("daily_verses").select("*").eq("verse_date", str(today)).eq("language", lang).execute()
            if res.data and len(res.data) > 0:
                row = res.data[0]
                return VerseResponse(success=True, data={
                    "text": row.get("verse_text"),
                    "ref": row.get("verse_reference"),
                    "theme": "Daily Bread"
                })
        except Exception as e:
            print(f"Warning: Failed to fetch VOTD from Supabase: {e}")
            
    # Deterministic fallback based on Julian date
    index = today.toordinal() % len(FALLBACK_VERSES)
    v = FALLBACK_VERSES[index]
    
    # Optionally save it so it's cached for the rest of the day
    if supabase_admin:
        try:
            supabase_admin.table("daily_verses").insert({
                "verse_date": str(today),
                "language": lang,
                "verse_reference": v["ref"],
                "verse_text": v["text"]
            }).execute()
        except Exception:
            pass # Ignore unique constraint violations if another worker just saved it
            
    return VerseResponse(success=True, data=v)
@router.get("/passage")
async def get_passage_api(
    book: str, 
    chapter: int, 
    version: str = None, 
    translation: str = None,
    current_user: str = Depends(get_current_user)
):
    """Fetches a full chapter of scripture."""
    version_code = version or translation or "en_kjv"
    try:
        from database.bible_loader import get_passage, normalize_book
        book_num = normalize_book(book)
        
        if not book_num:
             return {"success": False, "data": [], "error": f"Book '{book}' not found"}
             
        verses = get_passage(version_code, book_num, chapter)
        if not verses:
            return {"success": False, "data": [], "error": "Chapter not found"}
            
        # Standardize keys for the JSON response
        formatted_verses = [{"verse": v.get("verse"), "text": v.get("text")} for v in verses]
        return {"success": True, "data": formatted_verses, "error": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chapter-count")
async def get_chapter_count(
    book: str, 
    version: str = "en_kjv",
    current_user: str = Depends(get_current_user)
):
    """Returns the total number of chapters in a book."""
    version_code = version or "en_kjv" # translation parameter was removed, so simplify this line
    try:
        from database.bible_loader import get_chapter_count, BOOK_NAME_TO_NUM
        book_lower = book.lower().strip()
        book_num = BOOK_NAME_TO_NUM.get(book_lower)
        
        if not book_num:
            return {"success": False, "data": {"count": 50}, "error": "Book not found"}
            
        count = get_chapter_count(book_num, version_code=version_code)
        return {"success": True, "data": {"count": count}, "error": None}
    except Exception as e:
        return {"success": False, "data": {"count": 50}, "error": str(e)}
