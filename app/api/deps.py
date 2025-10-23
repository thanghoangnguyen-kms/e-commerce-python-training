from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.jwt import decode_token

security = HTTPBearer(
    scheme_name="Bearer",
    description="Enter your JWT token (the 'Bearer' prefix is automatically added)"
)

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Validates JWT token and returns user payload.
    Token is automatically extracted from Authorization header by FastAPI.
    """
    try:
        token = credentials.credentials
        payload = decode_token(token)
        return payload  # {"sub": user_id, "role": ...}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or missing token")

def admin_required(user=Depends(get_current_user)):
    """
    Requires user to be authenticated and have admin role.
    """
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user
