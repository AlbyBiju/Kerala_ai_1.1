from fastapi import APIRouter, HTTPException, status
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.config import settings
from app.core.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    is_username_valid = (request.username == settings.TEAM_USERNAME)
    is_password_valid = verify_password(request.password, settings.TEAM_PASSWORD)

    if not (is_username_valid and is_password_valid):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token(data={"sub": request.username})
    return TokenResponse(access_token=token, token_type="bearer")
