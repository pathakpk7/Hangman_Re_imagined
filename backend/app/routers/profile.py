from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.game import RealUserProfile, ModeStatItem
from backend.app.models_db import DBUser, DBUserHeartState, DBClassicProgress, DBModeStats
from backend.app.services.game_engine import game_engine

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("/{user_id}", response_model=RealUserProfile)
def get_user_profile(user_id: str, db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    hearts, secs = game_engine.calculate_heart_regen(user_id, db)
    
    classic_prog = db.query(DBClassicProgress).filter(DBClassicProgress.user_id == user_id).first()
    c_level = classic_prog.current_level if classic_prog else 1
    h_level = classic_prog.highest_level if classic_prog else 1
    total_xp = classic_prog.xp if classic_prog else 0
    cons_losses = classic_prog.consecutive_losses if classic_prog else 0

    mode_stats_db = db.query(DBModeStats).filter(DBModeStats.user_id == user_id).all()
    mode_stats_dict = {}
    category_stats_dict = {}

    for ms in mode_stats_db:
        item = ModeStatItem(
            games_played=ms.games_played,
            games_won=ms.games_won,
            games_lost=ms.games_lost,
            xp_earned=ms.xp_earned,
            best_score=ms.best_score,
            best_time_seconds=ms.best_time_seconds,
            total_words=ms.total_words_played,
            current_streak=ms.current_streak
        )
        if ms.mode == "category" and ms.category_name:
            category_stats_dict[ms.category_name] = item
        else:
            mode_stats_dict[ms.mode] = item

    # Ensure default entries exist if empty
    for default_mode in ["classic", "timed", "practice", "daily", "infinite"]:
        if default_mode not in mode_stats_dict:
            mode_stats_dict[default_mode] = ModeStatItem()

    return RealUserProfile(
        user_id=user.id,
        username=user.username,
        email=user.email,
        hearts_remaining=hearts,
        heart_regen_seconds_left=secs,
        classic_level=c_level,
        highest_classic_level=h_level,
        total_xp=total_xp,
        consecutive_losses=cons_losses,
        word_lifelines=user.word_lifelines or 2,
        lifeline_unlocked=(c_level >= 5),
        mode_stats=mode_stats_dict,
        category_stats=category_stats_dict
    )
