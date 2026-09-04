import jwt
from typing import Optional
from fastapi import Request, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.core.config import settings

security = HTTPBearer(auto_error=False)

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)):
    """
    Validates the Supabase JWT token from the Authorization header.
    Returns the user's UUID if valid.
    """
    if not credentials:
         # No token provided - return a default user for local testing if no secret is set
         if not settings.SUPABASE_JWT_SECRET:
             return "local_mvp_guest"
         raise HTTPException(status_code=401, detail="Authentication required")

    token = credentials.credentials
    if not settings.SUPABASE_JWT_SECRET:
        # Failsafe if the environment is not configured correctly
        # Extract the user ID without verifying signature so MVP still loads
        try:
            # Explicitly decode without verification for local development
            payload = jwt.decode(token, options={"verify_signature": False}, algorithms=["HS256"])
            return payload.get("sub", "local_mvp_user")
        except Exception as e:
            print(f"Auth Failsafe Trace: {e}")
            return "local_mvp_user"
        
    try:
        # Decode the JWT token using the Supabase JWT secret
        # Supabase uses HS256 algorithm by default.
        # "aud": "authenticated" is the standard audience for logged-in users.
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing subject (user id)")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
