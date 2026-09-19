from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.game import (
    StartGameRequest, GuessRequest, HintRequest, GameStateResponse, HintResponse, DailyChallengeResponse
)
from backend.app.services.game_engine import game_engine

router = APIRouter(prefix="/game", tags=["Game"])

@router.post("/start", response_model=GameStateResponse)
def start_game(req: StartGameRequest, db: Session = Depends(get_db)):
    session = game_engine.create_game(
        mode=req.mode,
        level=req.level or 1,
        category=req.category or "General",
        user_id=req.user_id,
        db=db
    )
    resp = session.to_response()
    if req.user_id:
        hearts, secs = game_engine.calculate_heart_regen(req.user_id, db)
        resp.lives_remaining = hearts
        resp.heart_regen_seconds_left = secs
    return resp

@router.post("/guess", response_model=GameStateResponse)
def make_guess(req: GuessRequest, db: Session = Depends(get_db)):
    session = game_engine.get_session(req.game_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game session not found")
    return session.process_guess(req.letter, db=db)

@router.post("/hint", response_model=HintResponse)
def request_hint(req: HintRequest):
    session = game_engine.get_session(req.game_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game session not found")
    step, clue_text = session.process_hint(req.hint_step or 1)
    return HintResponse(
        game_id=session.game_id,
        hint_step=step,
        clue_text=clue_text,
        game_state=session.to_response()
    )

@router.get("/daily", response_model=DailyChallengeResponse)
def get_daily_challenge(user_id: str = "anon"):
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    session = game_engine.create_daily_game(date_str=today_str, user_id=user_id)
    return DailyChallengeResponse(
        date=today_str,
        word_dna=session.get_word_dna(),
        game_id=session.game_id
    )
