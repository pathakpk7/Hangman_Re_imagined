from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.game import SignUpRequest, LoginRequest, AuthResponse
from backend.app.services.auth import create_user, authenticate_user
from backend.app.models_db import DBUser

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", response_model=AuthResponse)
def signup(req: SignUpRequest, db: Session = Depends(get_db)):
    try:
        user = create_user(db, email=req.email, username=req.username, password=req.password)
        return AuthResponse(
            token=f"token_{user.id}",
            user_id=user.id,
            username=user.username,
            email=user.email
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, req.email_or_username, req.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username/email or password")
    return AuthResponse(
        token=f"token_{user.id}",
        user_id=user.id,
        username=user.username,
        email=user.email
    )
