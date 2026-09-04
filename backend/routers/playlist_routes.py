from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from backend.core.supabase_client import supabase_admin
from backend.core.security import get_current_user

router = APIRouter(prefix="/api/playlists", tags=["playlists"])

class ActionResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class PlaylistsResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    error: Optional[Dict[str, Any]] = None

class PlaylistCreate(BaseModel):
    name: str

class PlaylistUpdate(BaseModel):
    name: str

class PlaylistSongCreate(BaseModel):
    song_id: str

def get_or_create_default_playlist(user_id: str) -> str:
    res = supabase_admin.table("playlists").select("id").eq("user_id", user_id).eq("name", "USER").execute()
    if res.data:
        return res.data[0]["id"]
    new_res = supabase_admin.table("playlists").insert({"name": "USER", "user_id": user_id}).execute()
    return new_res.data[0]["id"]

@router.get("", response_model=PlaylistsResponse)
async def get_playlists(current_user: str = Depends(get_current_user)):
    """
    Get all playlists for the current authenticated user.
    """
    if not supabase_admin:
        print("Warning: get_playlists called but Supabase not configured")
        return PlaylistsResponse(success=True, data=[])
        
    try:
        print(f"DEBUG: Fetching playlists for user {current_user}")
        res = supabase_admin.table("playlists").select("*").eq("user_id", current_user).order("created_at").execute()
        print(f"DB: Found {len(res.data)} playlists")
        return PlaylistsResponse(success=True, data=res.data)
    except Exception as e:
        print(f"ERROR: get_playlists failed: {e}")
        return PlaylistsResponse(success=False, data=[], error={"message": str(e)})

@router.post("", response_model=ActionResponse)
async def create_playlist(playlist: PlaylistCreate, current_user: str = Depends(get_current_user)):
    """
    Create a new playlist for the current user.
    """
    if not supabase_admin:
        raise HTTPException(status_code=500, detail="Database not configured")
        
    try:
        data = {
            "name": playlist.name.strip(),
            "user_id": current_user
        }
        res = supabase_admin.table("playlists").insert(data).execute()
        
        if not res.data:
            raise HTTPException(status_code=400, detail="Failed to create playlist")
            
        return ActionResponse(success=True, data=res.data[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{playlist_id}", response_model=ActionResponse)
async def update_playlist(playlist_id: str, playlist: PlaylistUpdate, current_user: str = Depends(get_current_user)):
    """
    Rename an existing playlist.
    """
    if not supabase_admin:
        raise HTTPException(status_code=500, detail="Database not configured")
        
    try:
        # Verify ownership
        pl = supabase_admin.table("playlists").select("user_id").eq("id", playlist_id).execute()
        if not pl.data or pl.data[0].get("user_id") != current_user:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        res = supabase_admin.table("playlists").update({"name": playlist.name.strip()}).eq("id", playlist_id).execute()
        return ActionResponse(success=True, data=res.data[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{playlist_id}", response_model=ActionResponse)
async def delete_playlist(playlist_id: str, current_user: str = Depends(get_current_user)):
    """
    Delete a playlist. Moves all songs in this playlist to the default "USER" playlist before deletion.
    """
    if not supabase_admin:
        raise HTTPException(status_code=500, detail="Database not configured")
        
    try:
        # Verify ownership
        pl = supabase_admin.table("playlists").select("user_id, name").eq("id", playlist_id).execute()
        if not pl.data or pl.data[0].get("user_id") != current_user:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        # Prevent deleting the default USER playlist if the user tries
        if pl.data[0].get("name") == "USER":
             raise HTTPException(status_code=400, detail="Cannot delete the default USER playlist")

        # 1. Ensure "USER" playlist exists
        default_pl_id = get_or_create_default_playlist(current_user)
        
        # 2. Get all songs in the current playlist
        songs_res = supabase_admin.table("playlist_songs").select("song_id").eq("playlist_id", playlist_id).execute()
        
        # 3. For each song, move it to USER playlist if it's not already there
        for item in songs_res.data:
            song_id = item["song_id"]
            # Check if already in USER playlist
            exists = supabase_admin.table("playlist_songs").select("id").eq("playlist_id", default_pl_id).eq("song_id", song_id).execute()
            if not exists.data:
                supabase_admin.table("playlist_songs").insert({"playlist_id": default_pl_id, "song_id": song_id}).execute()
        
        # 4. Delete all mappings for the old playlist
        supabase_admin.table("playlist_songs").delete().eq("playlist_id", playlist_id).execute()
        
        # 5. Finally delete the playlist itself
        supabase_admin.table("playlists").delete().eq("id", playlist_id).execute()
        
        return ActionResponse(success=True, data={"message": "Playlist deleted, songs moved to USER"})
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{playlist_id}/songs", response_model=PlaylistsResponse)
async def get_playlist_songs(playlist_id: str, current_user: str = Depends(get_current_user)):
    """
    Get all songs in a specific playlist.
    """
    if not supabase_admin:
        return PlaylistsResponse(success=True, data=[])
        
    try:
        # Verify user owns the playlist
        pl = supabase_admin.table("playlists").select("user_id").eq("id", playlist_id).execute()
        if not pl.data or pl.data[0].get("user_id") != current_user:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        # Join query to fetch songs through playlist_songs
        res = supabase_admin.table("playlist_songs") \
            .select("id, song_id, songs(*)") \
            .eq("playlist_id", playlist_id) \
            .execute()
            
        # Format the result nicely
        songs = []
        for linkage in res.data:
            song_detail = linkage.get("songs")
            if song_detail:
                # include the linkage ID if needed for removal, though song_id is enough
                song_detail["_playlist_song_id"] = linkage["id"]
                songs.append(song_detail)
                
        return PlaylistsResponse(success=True, data=songs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{playlist_id}/songs", response_model=ActionResponse)
async def add_song_to_playlist(playlist_id: str, link: PlaylistSongCreate, current_user: str = Depends(get_current_user)):
    """
    Adds an existing song to a playlist.
    """
    if not supabase_admin:
        raise HTTPException(status_code=500, detail="Database not configured")
        
    try:
        # Verify ownership
        pl = supabase_admin.table("playlists").select("user_id").eq("id", playlist_id).execute()
        if not pl.data or pl.data[0].get("user_id") != current_user:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        data = {
            "playlist_id": playlist_id,
            "song_id": link.song_id
        }
        res = supabase_admin.table("playlist_songs").insert(data).execute()
        
        if not res.data:
            raise HTTPException(status_code=400, detail="Failed to add song to playlist")
            
        return ActionResponse(success=True, data={"message": "Song added to playlist"})
    except Exception as e:
        # Check if error is unique constraint violation (already in playlist)
        err_msg = str(e).lower()
        if "unique constraint" in err_msg or "duplicate key" in err_msg:
             return ActionResponse(success=False, error={"message": "Song is already in this playlist"})
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{playlist_id}/songs/{song_id}", response_model=ActionResponse)
async def remove_song_from_playlist(playlist_id: str, song_id: str, current_user: str = Depends(get_current_user)):
    """
    Removes a song from a playlist without deleting the actual song.
    """
    if not supabase_admin:
        raise HTTPException(status_code=500, detail="Database not configured")
        
    try:
        # Verify ownership
        pl = supabase_admin.table("playlists").select("user_id").eq("id", playlist_id).execute()
        if not pl.data or pl.data[0].get("user_id") != current_user:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        supabase_admin.table("playlist_songs").delete().eq("playlist_id", playlist_id).eq("song_id", song_id).execute()
        return ActionResponse(success=True, data={"message": "Song removed from playlist"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
