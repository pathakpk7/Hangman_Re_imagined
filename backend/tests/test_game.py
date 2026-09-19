import uuid
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_auth_signup_and_login():
    uid = str(uuid.uuid4())[:8]
    email = f"tester_{uid}@example.com"
    username = f"tester_{uid}"

    # Signup
    signup_resp = client.post("/api/v1/auth/signup", json={
        "email": email,
        "username": username,
        "password": "password123"
    })
    assert signup_resp.status_code == 200
    user_data = signup_resp.json()
    assert "user_id" in user_data
    assert user_data["username"] == username

    # Login
    login_resp = client.post("/api/v1/auth/login", json={
        "email_or_username": username,
        "password": "password123"
    })
    assert login_resp.status_code == 200
    assert login_resp.json()["user_id"] == user_data["user_id"]

def test_start_game_5_hearts():
    response = client.post("/api/v1/game/start", json={"mode": "classic", "level": 1})
    assert response.status_code == 200
    data = response.json()
    assert "game_id" in data
    assert data["status"] == "in_progress"
    assert data["lives_remaining"] == 5
    assert data["level"] == 1
    assert data["tier_label"] == "Very Easy"

def test_make_guess_and_heart_deduction():
    start_resp = client.post("/api/v1/game/start", json={"mode": "classic", "level": 1})
    game_id = start_resp.json()["game_id"]

    # Guess a letter
    guess_resp = client.post("/api/v1/game/guess", json={"game_id": game_id, "letter": "z"})
    assert guess_resp.status_code == 200
    data = guess_resp.json()
    assert "z" in data["guessed_letters"]
    assert data["lives_remaining"] in [4, 5]

def test_request_hint_single_sentence():
    start_resp = client.post("/api/v1/game/start", json={"mode": "classic", "level": 1})
    game_id = start_resp.json()["game_id"]

    hint_resp = client.post("/api/v1/game/hint", json={"game_id": game_id})
    assert hint_resp.status_code == 200
    data = hint_resp.json()
    assert "clue_text" in data
    assert len(data["clue_text"]) > 0

def test_real_profile():
    uid = str(uuid.uuid4())[:8]
    email = f"prof_{uid}@example.com"
    username = f"prof_{uid}"

    signup_resp = client.post("/api/v1/auth/signup", json={
        "email": email,
        "username": username,
        "password": "password123"
    })
    user_id = signup_resp.json()["user_id"]

    prof_resp = client.get(f"/api/v1/profile/{user_id}")
    assert prof_resp.status_code == 200
    pdata = prof_resp.json()
    assert pdata["username"] == username
    assert pdata["hearts_remaining"] == 5
    assert pdata["classic_level"] == 1
    assert "classic" in pdata["mode_stats"]

def test_no_word_repetition_for_user():
    uid = str(uuid.uuid4())[:8]
    signup_resp = client.post("/api/v1/auth/signup", json={
        "email": f"norepeat_{uid}@example.com",
        "username": f"norepeat_{uid}",
        "password": "password123"
    })
    user_id = signup_resp.json()["user_id"]

    seen_words = set()
    for level in range(1, 11):
        start_resp = client.post("/api/v1/game/start", json={
            "mode": "classic",
            "level": level,
            "user_id": user_id
        })
        assert start_resp.status_code == 200
        game_id = start_resp.json()["game_id"]
        from backend.app.services.game_engine import game_engine
        session = game_engine.get_session(game_id)
        assert session is not None
        word = session.secret_word
        assert word not in seen_words, f"Word '{word}' was repeated for level {level}!"
        seen_words.add(word)
        
        # End game so history is recorded
        for char in list("abcdefghijklmnopqrstuvwxyz"):
            res = session.process_guess(char)
            if res.status != "in_progress":
                from backend.app.database import SessionLocal
                db = SessionLocal()
                session._handle_db_game_end(won=(res.status=="won"), db=db)
                db.close()
                break

