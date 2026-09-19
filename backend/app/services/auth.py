import hashlib
import os
import uuid
import time
from typing import Optional
from sqlalchemy.orm import Session
from backend.app.models_db import DBUser, DBUserHeartState, DBClassicProgress, DBModeStats

SECRET_KEY = os.getenv("JWT_SECRET", "hangman_reimagined_secret_key_2026")

def hash_password(password: str) -> str:
    return hashlib.sha256((password + SECRET_KEY).encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def create_user(db: Session, email: str, username: str, password: str) -> DBUser:
    existing_user = db.query(DBUser).filter((DBUser.email == email) | (DBUser.username == username)).first()
    if existing_user:
        raise ValueError("User with this email or username already exists.")

    user = DBUser(
        id=str(uuid.uuid4()),
        email=email.lower().strip(),
        username=username.strip(),
        hashed_password=hash_password(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Initialize Heart State (5 hearts max)
    heart_state = DBUserHeartState(user_id=user.id, hearts_remaining=5, last_regen_timestamp=time.time())
    db.add(heart_state)

    # Initialize Classic Progress (Level 1)
    classic_progress = DBClassicProgress(user_id=user.id, current_level=1, highest_level=1, xp=0)
    db.add(classic_progress)

    # Initialize Mode Stats for all modes
    modes = ["classic", "timed", "practice", "daily", "infinite"]
    for m in modes:
        db.add(DBModeStats(user_id=user.id, mode=m))

    db.commit()
    return user

def authenticate_user(db: Session, email_or_username: str, password: str) -> Optional[DBUser]:
    identifier = email_or_username.lower().strip()
    user = db.query(DBUser).filter((DBUser.email == identifier) | (DBUser.username == identifier)).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
