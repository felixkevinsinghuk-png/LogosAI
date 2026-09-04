from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, date

from backend.core.security import get_current_user
from backend.core.supabase_client import supabase_admin

router = APIRouter(prefix="/api/streak", tags=["streak"])

class StreakResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    error: Optional[Dict[str, Any]] = None

@router.post("/update", response_model=StreakResponse)
async def update_streak(current_user: str = Depends(get_current_user)):
    """
    Updates the user's daily streak and point total.
    Returns the current streak and points.
    """
    if not supabase_admin:
        return StreakResponse(success=True, data={"current_streak": 0, "total_points": 0})
        
    try:
        # Get current user stats
        res = supabase_admin.table("accountability_users").select("*").eq("user_id", current_user).execute()
        
        today = date.today()
        today_str = str(today)
        
        if not res.data:
            # First time using the system - initialize
            new_data = {
                "user_id": current_user,
                "current_streak": 1,
                "best_streak": 1,
                "total_points": 10,
                "last_active_date": today_str
            }
            supabase_admin.table("accountability_users").insert(new_data).execute()
            return StreakResponse(success=True, data=new_data)
            
        user_record = res.data[0]
        last_active_str = user_record.get("last_active_date")
        
        if last_active_str == today_str:
            # Already active today, no change
            return StreakResponse(success=True, data=user_record)
            
        # Parse last active date to check if it was exactly yesterday
        streak = user_record.get("current_streak", 0)
        points = user_record.get("total_points", 0)
        best = user_record.get("best_streak", 0)
        
        if last_active_str:
            last_active = datetime.strptime(last_active_str, "%Y-%m-%d").date()
            if today - last_active == timedelta(days=1):
                streak += 1
            else:
                streak = 1 # Streak broken
        else:
            streak = 1
            
        points += 10 # 10 points per daily login/activity
        
        if streak > best:
            best = streak
            
        update_data = {
            "current_streak": streak,
            "best_streak": best,
            "total_points": points,
            "last_active_date": today_str
        }
        
        updated = supabase_admin.table("accountability_users").update(update_data).eq("user_id", current_user).execute()
        
        return StreakResponse(success=True, data=updated.data[0] if updated.data else update_data)
        
    except Exception as e:
        print(f"Error updating streak: {e}")
        # Return fallback on error to not crash the frontend
        return StreakResponse(success=False, data={"current_streak": 0, "total_points": 0}, error={"message": str(e)})

@router.get("", response_model=StreakResponse)
async def get_streak(current_user: str = Depends(get_current_user)):
    """Fetches the user's current streak without modifying it."""
    if not supabase_admin:
        return StreakResponse(success=True, data={"current_streak": 0, "total_points": 0})
        
    try:
        res = supabase_admin.table("accountability_users").select("*").eq("user_id", current_user).execute()
        if res.data:
            return StreakResponse(success=True, data=res.data[0])
        return StreakResponse(success=True, data={"current_streak": 0, "total_points": 0})
    except Exception as e:
        return StreakResponse(success=False, data={"current_streak": 0, "total_points": 0}, error={"message": str(e)})
