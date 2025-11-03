from fastapi import APIRouter, Depends
from app.api.deps import admin_required, get_current_user
from app.api.service_deps import get_auth_service
from app.services.auth_service import AuthService
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    PromoteUserRequest
)

router = APIRouter()

@router.post("/signup", response_model=TokenResponse)
async def signup(data: SignupRequest, auth_service: AuthService = Depends(get_auth_service)):
    """Register a new user account and receive access token (expires in 15 minutes)."""
    result = await auth_service.signup_user(data.email, data.password)
    return TokenResponse(**result)

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    """Authenticate and receive access token (expires in 15 minutes)."""
    result = await auth_service.login_user(data.email, data.password)
    return TokenResponse(**result)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user=Depends(get_current_user), auth_service: AuthService = Depends(get_auth_service)):
    """
    Get current authenticated user information.

    Returns the user profile including role.
    """
    db_user = await auth_service.get_user_by_id(user["sub"])
    return UserResponse(
        id=str(db_user.id),
        email=db_user.email,
        role=db_user.role,
        created_at=db_user.created_at.isoformat()
    )

@router.post("/promote-to-admin", response_model=UserResponse)
async def promote_to_admin(data: PromoteUserRequest, admin_user=Depends(admin_required), auth_service: AuthService = Depends(get_auth_service)):
    """
    Promote a user to admin role (Admin only).

    Only existing admins can promote other users to admin.
    """
    user = await auth_service.promote_user_to_admin(data.email)
    return UserResponse(
        id=str(user.id),
        email=user.email,
        role=user.role,
        created_at=user.created_at.isoformat()
    )
