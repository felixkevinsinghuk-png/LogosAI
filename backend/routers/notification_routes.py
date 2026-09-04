from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from backend.core.security import get_current_user
from backend.core.supabase_client import supabase_admin

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

class NotificationResponse(BaseModel):
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    error: Optional[Dict[str, Any]] = None

@router.get("", response_model=NotificationResponse)
async def get_notifications(current_user: str = Depends(get_current_user)):
    """Fetches the user's notifications."""
    if not supabase_admin:
        return NotificationResponse(success=False, error={"message": "DB not configured"})
        
    try:
        res = supabase_admin.table("notifications").select("*").eq("user_id", current_user).order("created_at", desc=True).limit(20).execute()
        
        # If no notifications exist, provide a welcome mock so it's not empty for the MVP demo:
        if not res.data:
            welcome_notif = {
                "user_id": current_user,
                "title": "Welcome to RhemaLight AI!",
                "message": "We're glad to have you. Enjoy tracing your spiritual journey.",
                "type": "system",
                "is_read": False
            }
            supabase_admin.table("notifications").insert(welcome_notif).execute()
            res = supabase_admin.table("notifications").select("*").eq("user_id", current_user).order("created_at", desc=True).limit(20).execute()
            
        return NotificationResponse(success=True, data=res.data)
    except Exception as e:
        print(f"Error fetching notifications: {e}")
        return NotificationResponse(success=False, error={"message": str(e)})

@router.post("/{notif_id}/read", response_model=NotificationResponse)
async def mark_notification_read(notif_id: str, current_user: str = Depends(get_current_user)):
    """Marks a notification as read."""
    if not supabase_admin:
        return NotificationResponse(success=False, error={"message": "DB not configured"})
        
    try:
        res = supabase_admin.table("notifications").update({"is_read": True}).eq("id", notif_id).eq("user_id", current_user).execute()
        return NotificationResponse(success=True, data=res.data)
    except Exception as e:
        print(f"Error marking notification read: {e}")
        return NotificationResponse(success=False, error={"message": str(e)})
