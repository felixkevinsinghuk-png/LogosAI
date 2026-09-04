from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Any, Dict
from backend.core.supabase_client import supabase_admin
from backend.core.security import get_current_user

router = APIRouter(prefix="/api/songs", tags=["songs"])

class SongsResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    error: Optional[Dict[str, Any]] = None

class SongCreate(BaseModel):
    title: str
    category: str = "custom"
    language: str = "en"
    youtube_url: Optional[str] = None
    youtube_video_id: Optional[str] = None
    thumbnail_url: Optional[str] = None
    playlist_id: Optional[str] = None

class SongUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    youtube_url: Optional[str] = None
    youtube_video_id: Optional[str] = None
    thumbnail_url: Optional[str] = None
    playlist_id: Optional[str] = None

class ActionResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

# No default songs — users add their own via YouTube URL
INITIAL_SONGS = []

def get_or_create_default_playlist(user_id: str) -> Optional[str]:
    # If user is a guest, they can't have a private default playlist in the DB reliably
    # without a valid UUID. We'll return a null or handle it as a system playlist.
    if "-" not in user_id:
        return None

    res = supabase_admin.table("playlists").select("id").eq("user_id", user_id).eq("name", "USER").execute()
    if res.data:
        return res.data[0]["id"]
    new_res = supabase_admin.table("playlists").insert({"name": "USER", "user_id": user_id}).execute()
    return new_res.data[0]["id"]

def ensure_user_exists(user_id: str) -> bool:
    """Ensures the user has a row in public.users. Returns True on success."""
    if "-" not in user_id:
        return True  # Guest — no FK needed
    try:
        check = supabase_admin.table("users").select("id").eq("id", user_id).execute()
        if check.data:
            return True
        # Fetch email from auth admin
        email = None
        try:
            auth_user = supabase_admin.auth.admin.get_user_by_id(user_id)
            if auth_user and auth_user.user:
                email = auth_user.user.email
        except Exception:
            pass
        if not email:
            return False
        supabase_admin.table("users").insert({"id": user_id, "email": email, "theme": "light", "preferred_language": "en"}).execute()
        return True
    except Exception as e:
        print(f"ensure_user_exists error: {e}")
        return False

@router.get("", response_model=SongsResponse)
async def get_songs(
    category: Optional[str] = None, 
    lang: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """
    Fetches songs from Supabase.
    """
    if not supabase_admin:
        print("Warning: Fetching songs using INITIAL_SONGS (Supabase not configured)")
        return SongsResponse(success=True, data=INITIAL_SONGS)
        
    try:
        print(f"DEBUG: Fetching songs for user {current_user}")
        
        # Unified query - show system songs (no user_id) OR user's own songs
        query = supabase_admin.table("songs").select("*")
        
        # Only filter by user_id if it's a valid UUID (not 'local_mvp_guest')
        if "-" in current_user:
            query = query.or_(f"user_id.eq.{current_user},user_id.is.null")
        else:
            query = query.is_("user_id", "null")
        
        if category:
            query = query.eq("category", category)
        if lang:
            query = query.eq("language", lang)
            
        res = query.order("title").execute()
        print(f"DB: Found {len(res.data)} songs")
        
        # STEP 6 FIX: Filter out songs with NO youtube_video_id locally if they exist
        clean_data = [s for s in res.data if s.get("youtube_video_id")]
        if len(clean_data) < len(res.data):
             print(f"DB: Filtered {len(res.data) - len(clean_data)} invalid (no-video) songs")

        return SongsResponse(success=True, data=clean_data)
    except Exception as e:
        print(f"CRITICAL ERROR: get_songs failed: {e}")
        # Always return success=False if there's an actual exception, 
        # or success=True with fallback data if that's preferred.
        # Following Step 9: Always return a response.
        return SongsResponse(success=False, data=[], error={"message": str(e)})

@router.post("", response_model=ActionResponse)
async def add_song(song: SongCreate, current_user: str = Depends(get_current_user)):
    """
    Adds a custom song with YouTube metadata and assigns to a playlist.
    """
    if not supabase_admin:
        raise HTTPException(
            status_code=503,
            detail="Database not configured. To add songs, set SUPABASE_SERVICE_ROLE_KEY in your .env file. Get it from: Supabase Dashboard → Project Settings → API → Service Role Key."
        )
        
    try:
        print(f"DEBUG: Adding song for user {current_user}")
        # Ensure user row exists in public.users before song insert (FK requirement)
        if "-" in current_user:
            ensure_user_exists(current_user)
        data = {
            "title": song.title,
            "category": song.category,
            "language": song.language,
            "lyrics": "Lyrics available via video",
            "youtube_url": song.youtube_url,
            "youtube_video_id": song.youtube_video_id,
            "thumbnail_url": song.thumbnail_url,
            "user_id": current_user if "-" in current_user else None
        }
        res = supabase_admin.table("songs").insert(data).execute()
        
        print(f"DB: Insert response: {res}")
        
        if not res.data:
            print(f"CRITICAL: Insert failed - no data returned. Check RLS or constraints.")
            raise HTTPException(status_code=400, detail="Failed to add song to database (no return data)")
            
        new_song_id = res.data[0]["id"]
        print(f"DB: Created song {new_song_id}")
        
        # Handle playlist assignment
        target_playlist = song.playlist_id
        if not target_playlist or target_playlist == "USER":
            target_playlist = get_or_create_default_playlist(current_user)
            
        # Verify ownership of playlist if provided explicitly
        if target_playlist and song.playlist_id and song.playlist_id != "USER":
            pl_check = supabase_admin.table("playlists").select("user_id").eq("id", target_playlist).execute()
            if not pl_check.data or pl_check.data[0].get("user_id") != current_user:
                raise HTTPException(status_code=403, detail="Not authorized to add to this playlist")
                
        if target_playlist:
            print(f"DB: Assigning to playlist {target_playlist}")
            supabase_admin.table("playlist_songs").insert({"playlist_id": target_playlist, "song_id": new_song_id}).execute()
        
        return ActionResponse(success=True, data=res.data[0])
    except Exception as e:
        print(f"CRITICAL ERROR: add_song failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{song_id}", response_model=ActionResponse)
async def update_song(song_id: str, updates: SongUpdate, current_user: str = Depends(get_current_user)):
    """
    Updates song details and optionally moves it to a different playlist.
    """
    if not supabase_admin:
        raise HTTPException(status_code=500, detail="Database not configured")
        
    try:
        song = supabase_admin.table("songs").select("user_id").eq("id", song_id).execute()
        if not song.data or song.data[0].get("user_id") != current_user:
            raise HTTPException(status_code=403, detail="Not authorized to edit this song")
            
        update_data = {}
        if updates.title is not None: update_data["title"] = updates.title
        if updates.category is not None: update_data["category"] = updates.category
        if updates.youtube_video_id is not None: 
            update_data["youtube_video_id"] = updates.youtube_video_id
            update_data["youtube_url"] = updates.youtube_url
            update_data["thumbnail_url"] = updates.thumbnail_url
            
        if update_data:
            supabase_admin.table("songs").update(update_data).eq("id", song_id).execute()
            
        # Handle Playlist Move
        if updates.playlist_id:
            target_playlist = updates.playlist_id
            if target_playlist == "USER":
                target_playlist = get_or_create_default_playlist(current_user)
            else:
                pl_check = supabase_admin.table("playlists").select("user_id").eq("id", target_playlist).execute()
                if not pl_check.data or pl_check.data[0].get("user_id") != current_user:
                    raise HTTPException(status_code=403, detail="Not authorized for this playlist")
            
            # Delete old mappings for this song
            supabase_admin.table("playlist_songs").delete().eq("song_id", song_id).execute()
            # Insert new mapping
            supabase_admin.table("playlist_songs").insert({"playlist_id": target_playlist, "song_id": song_id}).execute()

        return ActionResponse(success=True, data={"message": "Song updated"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{song_id}", response_model=ActionResponse)
async def delete_song(song_id: str, current_user: str = Depends(get_current_user)):
    """
    Deletes a song. Validates that the current user owns the song.
    """
    if not supabase_admin:
        raise HTTPException(status_code=500, detail="Database not configured")
        
    try:
        song = supabase_admin.table("songs").select("user_id").eq("id", song_id).execute()
        if not song.data or song.data[0].get("user_id") != current_user:
            raise HTTPException(status_code=403, detail="Not authorized to delete this song")
            
        res = supabase_admin.table("songs").delete().eq("id", song_id).execute()
        return ActionResponse(success=True, data={"message": "Song deleted"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

