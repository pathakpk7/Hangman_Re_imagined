from fastapi import APIRouter, HTTPException, status
from backend.app.models.game import (
    CreateRoomRequest, JoinRoomRequest, RoomGuessRequest, RoomStateResponse
)
from backend.app.services.multiplayer_service import multiplayer_service

router = APIRouter(prefix="/multiplayer", tags=["Multiplayer"])

@router.post("/create", response_model=RoomStateResponse)
def create_room(req: CreateRoomRequest):
    return multiplayer_service.create_room(
        player_name=req.player_name,
        user_id=req.user_id,
        category=req.category or "General"
    )

@router.post("/join", response_model=RoomStateResponse)
def join_room(req: JoinRoomRequest):
    try:
        return multiplayer_service.join_room(
            room_code=req.room_code,
            player_name=req.player_name,
            user_id=req.user_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/room/{code}", response_model=RoomStateResponse)
def get_room_state(code: str):
    try:
        return multiplayer_service.get_room_state(code)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/guess", response_model=RoomStateResponse)
def make_room_guess(req: RoomGuessRequest):
    try:
        return multiplayer_service.process_room_guess(
            room_code=req.room_code,
            player_id=req.player_id,
            letter=req.letter
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
