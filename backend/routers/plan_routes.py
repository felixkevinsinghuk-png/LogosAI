from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime
from backend.core.security import get_current_user
from backend.core.supabase_client import supabase_admin

router = APIRouter(prefix="/api/plans", tags=["plans"])

# --- Models ---

class CommonResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

# --- Static Data: Plan Definitions & Readings ---

AVAILABLE_PLANS = {
    "nt-year": {
        "id": "nt-year",
        "title": "New Testament in a Year",
        "description": "Read through the entire New Testament in 365 days, one chapter a day.",
        "duration_days": 365,
        "readings": {i: f"Day {i} Reading" for i in range(1, 366)} # Simplified for now
    },
    "gospels-30": {
        "id": "gospels-30",
        "title": "Gospels in 30 Days",
        "description": "An intensive 30-day journey through Matthew, Mark, Luke, and John.",
        "duration_days": 30,
        "readings": {
            1: "Matthew 1-3", 2: "Matthew 4-6", 3: "Matthew 7-9", 4: "Matthew 10-12", 5: "Matthew 13-15",
            6: "Matthew 16-18", 7: "Matthew 19-21", 8: "Matthew 22-24", 9: "Matthew 25-27", 10: "Matthew 28",
            11: "Mark 1-2", 12: "Mark 3-4", 13: "Mark 5-6", 14: "Mark 7-8", 15: "Mark 9-10",
            16: "Mark 11-12", 17: "Mark 13-14", 18: "Mark 15-16", 19: "Luke 1-2", 20: "Luke 3-4",
            21: "Luke 5-6", 22: "Luke 7-8", 23: "Luke 9-10", 24: "Luke 11-12", 25: "Luke 13-14",
            26: "Luke 15-16", 27: "Luke 17-18", 28: "Luke 19-20", 29: "Luke 21-22", 30: "Luke 23-24"
        }
    },
    "psalms-proverbs": {
        "id": "psalms-proverbs",
        "title": "Psalms & Proverbs",
        "description": "Daily wisdom and worship reading a Psalm and a Proverb each day.",
        "duration_days": 150,
        "readings": {i: f"Psalm {i} & Proverb {((i-1)%31)+1}" for i in range(1, 151)}
    }
}

# --- Endpoints ---

@router.get("", response_model=CommonResponse)
async def get_plans():
    """Returns available reading plans metadata."""
    return CommonResponse(success=True, data=list(AVAILABLE_PLANS.values()))

@router.get("/progress", response_model=CommonResponse)
async def get_all_progress(current_user: str = Depends(get_current_user)):
    """Gets overall progress percentage for all plans the user has started."""
    if not supabase_admin: return CommonResponse(success=True, data={})
    if "-" not in current_user: return CommonResponse(success=True, data={})
    
    try:
        # Fetch all completion records for this user
        res = supabase_admin.table("reading_progress").select("plan_id, completed").eq("user_id", current_user).execute()
        
        # Calculate percentages
        progress_map = {}
        for row in res.data:
            pid = row["plan_id"]
            if pid not in progress_map:
                progress_map[pid] = {"completed": 0, "total": AVAILABLE_PLANS.get(pid, {}).get("duration_days", 1)}
            
            if row["completed"]:
                progress_map[pid]["completed"] += 1
        
        # Format for frontend
        result = {}
        for pid, stats in progress_map.items():
            result[pid] = {
                "percentage": round((stats["completed"] / stats["total"]) * 100, 2),
                "active": stats["completed"] > 0 or stats["total"] > 0 # Actually started if we have records
            }
            
        return CommonResponse(success=True, data=result)
    except Exception as e:
        return CommonResponse(success=False, error={"message": str(e)})

@router.post("/{plan_id}/start", response_model=CommonResponse)
async def start_plan(plan_id: str, current_user: str = Depends(get_current_user)):
    """Initializes a plan for the user by creating records for all days."""
    if plan_id not in AVAILABLE_PLANS:
        raise HTTPException(status_code=404, detail="Plan not found")
        
    duration = AVAILABLE_PLANS[plan_id]["duration_days"]
    if "-" not in current_user:
        return CommonResponse(success=True, data={"message": "Guest mode: progress not saved to cloud"})
    
    try:
        # Batch insert all days (idempotent via UNIQUE constraint in SQL)
        # However, for simplicity and to avoid bulk overhead if already started, check first
        existing = supabase_admin.table("reading_progress").select("id").eq("user_id", current_user).eq("plan_id", plan_id).limit(1).execute()
        
        if not existing.data:
            batch = [
                {
                    "user_id": current_user,
                    "plan_id": plan_id,
                    "day_number": d,
                    "completed": False
                } for d in range(1, duration + 1)
            ]
            # Use chunks if duration is very high (e.g. 365) to be safe
            for i in range(0, len(batch), 100):
                supabase_admin.table("reading_progress").insert(batch[i:i+100]).execute()
        
        return CommonResponse(success=True, data={"message": "Plan initialized"})
    except Exception as e:
        return CommonResponse(success=False, error={"message": str(e)})

@router.get("/{plan_id}/next", response_model=CommonResponse)
async def get_next_day(plan_id: str, current_user: str = Depends(get_current_user)):
    """Finds the next incomplete day and its reading content."""
    if "-" not in current_user:
        # Default to day 1 for guests
        reading = AVAILABLE_PLANS.get(plan_id, {}).get("readings", {}).get(1, "No reading defined")
        return CommonResponse(success=True, data={
            "day_number": 1,
            "reading": reading,
            "plan_title": AVAILABLE_PLANS.get(plan_id, {}).get("title")
        })

    try:
        res = supabase_admin.table("reading_progress")\
            .select("day_number")\
            .eq("user_id", current_user)\
            .eq("plan_id", plan_id)\
            .eq("completed", False)\
            .order("day_number", desc=False)\
            .limit(1)\
            .execute()
        
        # If no incomplete rows AND rows exist → finished
        # If NO rows at all → auto-start at day 1 (plan wasn't initialized)
        if not res.data:
            all_res = supabase_admin.table("reading_progress")\
                .select("id")\
                .eq("user_id", current_user)\
                .eq("plan_id", plan_id)\
                .limit(1)\
                .execute()
            if all_res.data:
                # Has rows, but all completed → finished!
                return CommonResponse(success=True, data={"finished": True})
            else:
                # No rows at all - plan not initialized, default to day 1
                day_num = 1
        else:
            day_num = res.data[0]["day_number"]
            
        reading = AVAILABLE_PLANS.get(plan_id, {}).get("readings", {}).get(day_num, "No reading defined")
        
        return CommonResponse(success=True, data={
            "day_number": day_num,
            "reading": reading,
            "plan_title": AVAILABLE_PLANS.get(plan_id, {}).get("title")
        })
    except Exception as e:
        return CommonResponse(success=False, error={"message": str(e)})

@router.post("/{plan_id}/days/{day}/complete", response_model=CommonResponse)
async def complete_day(plan_id: str, day: int, current_user: str = Depends(get_current_user)):
    """Marks a specific day as completed and returns updated overall progress."""
    if "-" not in current_user:
        return CommonResponse(success=True, data={
            "completed_days": 1,
            "total_days": AVAILABLE_PLANS.get(plan_id, {}).get("duration_days", 30),
            "progress": 3 # Hardcoded 3% for guest visual feedback
        })

    try:
        # UPSERT so it works even if start_plan was never called or failed
        supabase_admin.table("reading_progress").upsert(
            {
                "user_id": current_user,
                "plan_id": plan_id,
                "day_number": day,
                "completed": True,
                "completed_at": datetime.now().isoformat()
            },
            on_conflict="user_id,plan_id,day_number"
        ).execute()
            
        # Recalculate progress for this plan
        stats_res = supabase_admin.table("reading_progress")\
            .select("completed")\
            .eq("user_id", current_user)\
            .eq("plan_id", plan_id)\
            .execute()
            
        completed_count = sum(1 for r in stats_res.data if r["completed"])
        total_count = AVAILABLE_PLANS[plan_id]["duration_days"]
        
        # Ensure at least 1% shows when any day is done; cap at 100% only when truly finished
        if completed_count == 0:
            progress_pct = 0
        elif completed_count >= total_count:
            progress_pct = 100
        else:
            progress_pct = round((completed_count / total_count) * 100, 2)
        
        return CommonResponse(success=True, data={
            "completed_days": completed_count,
            "total_days": total_count,
            "progress": progress_pct
        })
    except Exception as e:
        print(f"[Plans] complete_day error: {e}")
        return CommonResponse(success=False, error={"message": str(e)})

