from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.game import (
    StartGameRequest, GuessRequest, HintRequest, LifelineRequest, GameStateResponse, HintResponse, LifelineResponse, DailyChallengeResponse
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
    resp = session.to_response(db=db)
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
def request_hint(req: HintRequest, db: Session = Depends(get_db)):
    session = game_engine.get_session(req.game_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game session not found")
    step, clue_text = session.process_hint(req.hint_step or 1)
    return HintResponse(
        game_id=session.game_id,
        hint_step=step,
        clue_text=clue_text,
        game_state=session.to_response(db=db)
    )

@router.post("/lifeline", response_model=LifelineResponse)
def request_lifeline(req: LifelineRequest, db: Session = Depends(get_db)):
    session = game_engine.get_session(req.game_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game session not found")
    try:
        rev_char, rev_pos, str_clue, rem_lifelines = session.process_lifeline(option=req.option, db=db)
        return LifelineResponse(
            game_id=session.game_id,
            option=req.option,
            revealed_letter=rev_char,
            revealed_position=rev_pos,
            striking_clue=str_clue,
            word_lifelines_remaining=rem_lifelines,
            game_state=session.to_response(db=db)
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/daily", response_model=DailyChallengeResponse)
def get_daily_challenge(user_id: str = "anon"):
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    session = game_engine.create_daily_game(date_str=today_str, user_id=user_id)
    return DailyChallengeResponse(
        date=today_str,
        word_dna=session.get_word_dna(),
        game_id=session.game_id
    )
