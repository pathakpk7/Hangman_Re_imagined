import uuid
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_codex_service_flow():
    uid = f"user_{uuid.uuid4().hex[:6]}"
    signup_resp = client.post("/api/v1/auth/signup", json={
        "email": f"{uid}@example.com",
        "username": uid,
        "password": "password123"
    })
    assert signup_resp.status_code == 200
    user_id = signup_resp.json()["user_id"]

    # Play a game with user_id
    start_resp = client.post("/api/v1/game/start", json={"mode": "classic", "level": 1, "user_id": user_id})
    assert start_resp.status_code == 200

    # Fetch codex
    codex_resp = client.get(f"/api/v1/codex/{user_id}")
    assert codex_resp.status_code == 200
    data = codex_resp.json()
    assert "total_unlocked" in data
    assert "items" in data

def test_multiplayer_1v1_flow():
    # Create room
    create_resp = client.post("/api/v1/multiplayer/create", json={
        "player_name": "Alice",
        "category": "Technology"
    })
    assert create_resp.status_code == 200
    room_data = create_resp.json()
    room_code = room_data["room_code"]
    p1_id = room_data["player1_id"]
    assert room_data["status"] == "waiting_for_player2"

    # Join room
    join_resp = client.post("/api/v1/multiplayer/join", json={
        "room_code": room_code,
        "player_name": "Bob"
    })
    assert join_resp.status_code == 200
    jdata = join_resp.json()
    assert jdata["status"] == "in_progress"
    p2_id = jdata["player2_id"]

    # Player 1 makes a guess
    guess_resp = client.post("/api/v1/multiplayer/guess", json={
        "room_code": room_code,
        "player_id": p1_id,
        "letter": "e"
    })
    assert guess_resp.status_code == 200
    gdata = guess_resp.json()
    assert "e" in gdata["guessed_letters"]
