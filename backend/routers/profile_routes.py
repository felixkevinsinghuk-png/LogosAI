from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from backend.core.security import get_current_user
from backend.core.supabase_client import supabase_admin

router = APIRouter(prefix="/api/profile", tags=["profile"])

class ProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    preferred_language: Optional[str] = None
    theme: Optional[str] = None

class ProfileResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

@router.get("/me", response_model=ProfileResponse)
async def get_profile(current_user: str = Depends(get_current_user)):
    """Fetches the user's profile."""
    if not supabase_admin:
        return ProfileResponse(success=False, error={"message": "DB not configured"})
        
    try:
        # GUEST MODE: If not a valid UUID format, return a default Guest profile
        if "-" not in current_user:
            return ProfileResponse(success=True, data={
                "id": "guest",
                "display_name": "Guest Explorer",
                "email": "guest@rhcemalight.ai",
                "preferred_language": "en",
                "theme": "light"
            })

        res = supabase_admin.table("users").select("*").eq("id", current_user).execute()
        if res.data:
            return ProfileResponse(success=True, data=res.data[0])
            
        # User is authenticated but has no public profile yet — auto-create it.
        # Fetch their email from auth admin API
        email = None
        try:
            auth_user = supabase_admin.auth.admin.get_user_by_id(current_user)
            if auth_user and auth_user.user:
                email = auth_user.user.email
        except Exception as auth_err:
            print(f"Warning: Could not fetch auth user email: {auth_err}")

        if not email:
            # Can't create profile without an email — return partial data
            return ProfileResponse(success=True, data={"id": current_user, "email": None})

        new_profile = {
            "id": current_user,
            "email": email,
            "theme": "light",
            "preferred_language": "en"
        }
        inserted = supabase_admin.table("users").insert(new_profile).execute()
        return ProfileResponse(success=True, data=inserted.data[0] if inserted.data else new_profile)
    except Exception as e:
        print(f"Error fetching profile: {e}")
        return ProfileResponse(success=False, error={"message": str(e)})

@router.patch("/me", response_model=ProfileResponse)
async def update_profile(req: ProfileUpdate, current_user: str = Depends(get_current_user)):
    """Updates the user's profile preferences."""
    if not supabase_admin:
        return ProfileResponse(success=False, error={"message": "DB not configured"})
        
    if "-" not in current_user:
        return ProfileResponse(success=False, error={"message": "Guests cannot update profile settings. Please log in."})

    try:
        update_data = {}
        if req.display_name is not None:
            update_data["display_name"] = req.display_name
        if req.preferred_language is not None:
            update_data["preferred_language"] = req.preferred_language
        if req.theme is not None:
            update_data["theme"] = req.theme
            
        if not update_data:
            return ProfileResponse(success=True, data={"message": "No fields to update"})
            
        # Ensure row exists
        check = supabase_admin.table("users").select("id").eq("id", current_user).execute()
        if not check.data:
            insert_data = {"id": current_user, **update_data}
            res = supabase_admin.table("users").insert(insert_data).execute()
        else:
            res = supabase_admin.table("users").update(update_data).eq("id", current_user).execute()
            
        return ProfileResponse(success=True, data=res.data[0] if res.data else update_data)
    except Exception as e:
        print(f"Error updating profile: {e}")
        return ProfileResponse(success=False, error={"message": str(e)})
