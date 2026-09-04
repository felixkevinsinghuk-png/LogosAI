import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def fix_songs():
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set in .env")
        return

    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    print("--- Worship Hub Data Fix ---")
    
    # 1. Find songs with missing youtube_video_id
    res = supabase.table("songs").select("id, title").is_("youtube_video_id", "null").execute()
    
    if not res.data:
        print("✅ No invalid songs found (all have YouTube IDs).")
    else:
        print(f"Found {len(res.data)} songs missing YouTube data.")
        for song in res.data:
            print(f"  - Deleting/Fixing: {song['title']} ({song['id']})")
            # For now, we delete them to prevent 'Infinite Loading' or playback errors
            # The user can re-add them using the new strict tool.
            supabase.table("songs").delete().eq("id", song["id"]).execute()
        print(f"Successfully cleaned up {len(res.data)} legacy records.")

    print("\n--- Syncing Initial Songs ---")
    # Optional: Re-seed initial songs if they are missing
    INITIAL_SONGS = [
        {"title": "10,000 Reasons", "youtube_video_id": "DXDGE_lRI0E", "youtube_url": "https://youtube.com/watch?v=DXDGE_lRI0E", "category": "praise", "language": "en"},
        {"title": "How Great Is Our God", "youtube_video_id": "K8cVnEaZ3lI", "youtube_url": "https://youtube.com/watch?v=K8cVnEaZ3lI", "category": "praise", "language": "en"}
    ]
    
    for s in INITIAL_SONGS:
        exists = supabase.table("songs").select("id").eq("title", s["title"]).execute()
        if not exists.data:
            supabase.table("songs").insert(s).execute()
            print(f"  + Re-seeded: {s['title']}")

    print("\nDone! Please restart your FastAPI server.")

if __name__ == "__main__":
    fix_songs()
