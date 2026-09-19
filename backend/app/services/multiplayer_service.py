import uuid
import random
import string
from typing import Dict, Any, Optional
from backend.app.services.word_service import word_service
from backend.app.models.game import RoomStateResponse, WordDna

class RoomSession:
    def __init__(self, room_code: str, player1_name: str, player1_id: Optional[str] = None, category: str = "General"):
        self.room_code = room_code.upper()
        self.player1_id = player1_id or f"p1_{uuid.uuid4().hex[:8]}"
        self.player1_name = player1_name or "Player 1"
        self.player1_score = 0

        self.player2_id: Optional[str] = None
        self.player2_name: Optional[str] = None
        self.player2_score = 0

        self.current_turn_player_id = self.player1_id

        # Pick a word for the duel
        self.word_data = word_service.select_word(difficulty=2, category=category)
        self.secret_word = self.word_data['word'].lower()
        self.length = len(self.secret_word)

        self.guessed_letters = set()
        self.lives_remaining = 5
        self.status = "waiting_for_player2" # waiting_for_player2, in_progress, won, lost

        self.winner_id: Optional[str] = None
        self.winner_name: Optional[str] = None

    def get_masked_word(self) -> list[str]:
        return [c if c in self.guessed_letters else "_" for c in self.secret_word]

    def get_word_dna(self) -> WordDna:
        return WordDna(
            length=self.word_data['length'],
            vowels=self.word_data['vowel_count'],
            consonants=self.word_data['consonant_count'],
            has_repeated_letters=self.word_data['has_repeated_letters'],
            category=self.word_data['category'],
            part_of_speech=self.word_data['part_of_speech']
        )

    def to_response(self) -> RoomStateResponse:
        turn_name = self.player1_name if self.current_turn_player_id == self.player1_id else (self.player2_name or "Player 2")
        return RoomStateResponse(
            room_code=self.room_code,
            player1_id=self.player1_id,
            player1_name=self.player1_name,
            player1_score=self.player1_score,
            player2_id=self.player2_id,
            player2_name=self.player2_name,
            player2_score=self.player2_score,
            current_turn_player_id=self.current_turn_player_id,
            current_turn_player_name=turn_name,
            masked_word=self.get_masked_word(),
            guessed_letters=sorted(list(self.guessed_letters)),
            lives_remaining=self.lives_remaining,
            status=self.status,
            word_dna=self.get_word_dna(),
            winner_id=self.winner_id,
            winner_name=self.winner_name,
        )

class MultiplayerService:
    def __init__(self):
        self._rooms: Dict[str, RoomSession] = {}

    def _generate_code(self) -> str:
        chars = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choices(chars, k=6))
            if code not in self._rooms:
                return code

    def create_room(self, player_name: str, user_id: Optional[str] = None, category: str = "General") -> RoomStateResponse:
        code = self._generate_code()
        session = RoomSession(room_code=code, player1_name=player_name, player1_id=user_id, category=category)
        self._rooms[code] = session
        return session.to_response()

    def join_room(self, room_code: str, player_name: str, user_id: Optional[str] = None) -> RoomStateResponse:
        code = room_code.upper()
        if code not in self._rooms:
            raise ValueError("Room code not found")

        session = self._rooms[code]
        if session.player2_id and session.player2_id != user_id:
            # Room is already full unless user is reconnecting
            if session.status != "waiting_for_player2":
                raise ValueError("Room is already full")

        session.player2_id = user_id or f"p2_{uuid.uuid4().hex[:8]}"
        session.player2_name = player_name or "Player 2"
        session.status = "in_progress"

        return session.to_response()

    def get_room_state(self, room_code: str) -> RoomStateResponse:
        code = room_code.upper()
        if code not in self._rooms:
            raise ValueError("Room code not found")
        return self._rooms[code].to_response()

    def process_room_guess(self, room_code: str, player_id: str, letter: str) -> RoomStateResponse:
        code = room_code.upper()
        if code not in self._rooms:
            raise ValueError("Room code not found")

        session = self._rooms[code]
        if session.status != "in_progress":
            return session.to_response()

        if session.current_turn_player_id != player_id:
            raise ValueError("It is not your turn!")

        letter = letter.lower()
        if letter in session.guessed_letters:
            return session.to_response()

        session.guessed_letters.add(letter)

        if letter in session.secret_word:
            occurrences = session.secret_word.count(letter)
            gained = 20 * occurrences
            if player_id == session.player1_id:
                session.player1_score += gained
            else:
                session.player2_score += gained

            # Check if word is completely guessed
            if all(c in session.guessed_letters for c in session.secret_word):
                session.status = "won"
                if session.player1_score >= session.player2_score:
                    session.winner_id = session.player1_id
                    session.winner_name = session.player1_name
                else:
                    session.winner_id = session.player2_id
                    session.winner_name = session.player2_name
        else:
            session.lives_remaining -= 1
            if session.lives_remaining <= 0:
                session.status = "lost"

            # Switch turn to opponent on incorrect guess
            if session.player2_id:
                session.current_turn_player_id = session.player2_id if session.current_turn_player_id == session.player1_id else session.player1_id

        return session.to_response()

multiplayer_service = MultiplayerService()
