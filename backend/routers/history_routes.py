from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime

from backend.core.security import get_current_user
from backend.core.supabase_client import supabase_admin

router = APIRouter(prefix="/api/history", tags=["history"])

class HistoryItem(BaseModel):
    id: str
    type: str
    title: str
    content: Optional[str] = None
    created_at: datetime

class HistoryResponse(BaseModel):
    success: bool
    data: List[HistoryItem]
    error: Optional[Dict[str, Any]] = None

@router.get("", response_model=HistoryResponse)
async def get_user_history(
    type: str = Query("all", description="Type of history: all, prayers, sermons, liked_verses"),
    limit: int = Query(20, ge=1, le=100),
    current_user: str = Depends(get_current_user)
):
    """
    Fetches the authenticated user's history (prayers, sermons, liked verses) from Supabase.
    """
    if not supabase_admin:
        raise HTTPException(status_code=500, detail="Database is not configured natively.")
        
    items = []
    
    try:
        if type in ["all", "prayers"]:
            res = supabase_admin.table("prayer_logs").select("*").eq("user_id", current_user).order("created_at", desc=True).limit(limit).execute()
            for row in res.data:
                items.append(HistoryItem(
                    id=row.get("id"),
                    type="prayer",
                    title="Prayer Log",
                    content=row.get("content"),
                    created_at=row.get("created_at")
                ))
                
        if type in ["all", "sermons"]:
            res = supabase_admin.table("sermons").select("*").eq("user_id", current_user).order("created_at", desc=True).limit(limit).execute()
            for row in res.data:
                topic = row.get("topic", "Untitled Sermon")
                # Exclude the massive HTML blob from the list view to save bandwidth
                items.append(HistoryItem(
                    id=row.get("id"),
                    type="sermon",
                    title=f"Sermon: {topic}",
                    content=row.get("verse_context"),
                    created_at=row.get("created_at")
                ))
                
        if type in ["all", "liked_verses"]:
            res = supabase_admin.table("verse_likes").select("*").eq("user_id", current_user).order("created_at", desc=True).limit(limit).execute()
            for row in res.data:
                items.append(HistoryItem(
                    id=row.get("id"),
                    type="verse_like",
                    title=row.get("verse_reference"),
                    content=row.get("verse_text"),
                    created_at=row.get("created_at")
                ))
                
        # Sort combined results descending
        items.sort(key=lambda x: x.created_at, reverse=True)
        # Apply combined limit
        items = items[:limit]
        
        return HistoryResponse(success=True, data=items)
        
    except Exception as e:
        print(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
