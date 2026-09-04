from supabase import create_client, Client
from backend.core.config import settings

def get_supabase() -> Client:
    """
    Returns an initialized Supabase client using the Service Role Key.
    This client bypasses Row Level Security constraints, so it should
    only be used in backend routes where permissions are manually
    asserted or when syncing server-side logic (like notifications).
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        print("Warning: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY is not set.")
        # We don't raise an error immediately on import to allow the server to start
        # when working purely locally or ignoring database features temporarily.
        return None
    
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

supabase_admin = get_supabase()
