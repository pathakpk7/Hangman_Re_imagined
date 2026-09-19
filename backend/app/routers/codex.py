from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.game import CodexListResponse
from backend.app.services.codex_service import codex_service

router = APIRouter(prefix="/codex", tags=["Codex"])

@router.get("/{user_id}", response_model=CodexListResponse)
def get_user_codex(
    user_id: str,
    q: Optional[str] = Query(None, description="Search query string"),
    category: Optional[str] = Query(None, description="Category filter"),
    db: Session = Depends(get_db)
):
    return codex_service.get_user_codex(user_id=user_id, query=q, category=category, db=db)
