import uuid
import time
import random
import re
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from backend.app.models.game import (
    GameStateResponse, WordDna, KnowledgeCard, HintResponse, WittyLossPopupPayload
)
from backend.app.services.word_service import word_service
from backend.app.services.level_service import level_service
from backend.app.services.codex_service import codex_service
from backend.app.models_db import DBUserHeartState, DBClassicProgress, DBModeStats, DBGameHistory, DBUserCodex

WITTY_LOSS_MESSAGES = [
    "Five words. Five defeats. At this point, the dictionary is starting to feel personally attacked.",
    "0 for 5! Have you considered trying an alphabet with fewer letters?",
    "Five consecutive losses! Don't worry, even Shakespeare had bad days... probably not 5 in a row though!",
    "Five strikes! The Hangman is considering giving you a cheat sheet.",
    "A 5-game loss streak! Time to grab a coffee, relax, and rebuild your vocabulary strength."
]

HEART_REGEN_INTERVAL_SECONDS = 120  # 1 heart every 2 minutes
MAX_HEARTS = 5

class GameSession:
    def __init__(self, game_id: str, mode: str, word_data: Dict[str, Any], level: int = 1, user_id: Optional[str] = None):
        self.game_id = game_id
        self.mode = mode
        self.level = level
        self.user_id = user_id
        self.word_data = word_data
        self.secret_word = word_data['word'].lower()
        self.length = len(self.secret_word)
        
        self.guessed_letters = set()
        self.revealed_indices = set()
        self.lives_remaining = 5  # Exactly 5 hearts for Classic/Standard games
        self.score = 0
        self.combo = 0
        self.mistakes = 0
        self.status = "in_progress"  # in_progress, won, lost

        # 3 Progressive Clues (None of which reveal the secret word)
        self.clue1_definition: Optional[str] = None
        self.clue2_sentence: Optional[str] = None
        self.clue3_context: Optional[str] = None

        self.start_time = time.time()
        self.witty_popup: Optional[WittyLossPopupPayload] = None

    def get_masked_word(self) -> List[str]:
        return [c if (i in self.revealed_indices or c in self.guessed_letters) else "_" for i, c in enumerate(self.secret_word)]

    def get_word_dna(self) -> WordDna:
        return WordDna(
            length=self.word_data['length'],
            vowels=self.word_data['vowel_count'],
            consonants=self.word_data['consonant_count'],
            has_repeated_letters=self.word_data['has_repeated_letters'],
            category=self.word_data['category'],
            part_of_speech=self.word_data['part_of_speech']
        )

    def process_guess(self, letter: str, db: Optional[Session] = None) -> GameStateResponse:
        letter = letter.lower()
        if self.status != "in_progress":
            return self.to_response()

        if letter in self.guessed_letters:
            return self.to_response()

        self.guessed_letters.add(letter)

        if letter in self.secret_word:
            self.combo += 1
            occurrences = [i for i, c in enumerate(self.secret_word) if c == letter]
            for idx in occurrences:
                self.revealed_indices.add(idx)

            base_points = 20 * len(occurrences)
            combo_multiplier = 1 + (self.combo * 0.2)
            difficulty_mult = 1 + (self.word_data.get('difficulty', 2) - 1) * 0.25
            
            added_score = int(base_points * combo_multiplier * difficulty_mult)
            self.score += added_score

            if len(self.revealed_indices) == self.length or all(c in self.guessed_letters for c in self.secret_word):
                self.status = "won"
                win_bonus = 100 * self.lives_remaining
                self.score += win_bonus
                if db and self.user_id:
                    self._handle_db_game_end(won=True, db=db)
        else:
            self.combo = 0
            self.mistakes += 1
            self.lives_remaining -= 1

            if self.lives_remaining <= 0:
                self.status = "lost"
                if db and self.user_id:
                    self._handle_db_game_end(won=False, db=db)

        return self.to_response()

    def process_hint(self, hint_step: int = 1) -> tuple[int, str]:
        """Generates 3 progressive clues without ever revealing the secret word"""
        clue_text = ""

        if hint_step == 1:
            def_str = self.word_data.get('definition', 'A term in vocabulary.')
            self.clue1_definition = f"Meaning: {def_str}"
            clue_text = self.clue1_definition

        elif hint_step == 2:
            raw_sent = self.word_data.get('example_sentence', f"In context, the term ___ plays an important role.")
            # Ensure target secret word is masked as ___ in sentence
            pattern = re.compile(re.escape(self.secret_word), re.IGNORECASE)
            masked_sent = pattern.sub("___", raw_sent)
            self.clue2_sentence = f"Context Sentence: \"{masked_sent}\""
            clue_text = self.clue2_sentence

        else:
            cat_str = self.word_data.get('category', 'General')
            pos_str = self.word_data.get('part_of_speech', 'word')
            syns = self.word_data.get('synonyms', [])
            syn_str = ", ".join(syns[:3]) if syns else "No direct synonyms"
            self.clue3_context = f"Category & Context: [{cat_str} - {pos_str}] · Synonyms: {syn_str}"
            clue_text = self.clue3_context

        return hint_step, clue_text

    def _handle_db_game_end(self, won: bool, db: Session):
        if not self.user_id:
            return

        codex_service.record_word_encounter(self.user_id, self.word_data, won, db)

        mode_stat = db.query(DBModeStats).filter(DBModeStats.user_id == self.user_id, DBModeStats.mode == self.mode).first()
        if not mode_stat:
            mode_stat = DBModeStats(user_id=self.user_id, mode=self.mode)
            db.add(mode_stat)

        mode_stat.games_played += 1
        if won:
            mode_stat.games_won += 1
            mode_stat.current_streak += 1
            mode_stat.xp_earned += self.score
            if self.score > mode_stat.best_score:
                mode_stat.best_score = self.score
        else:
            mode_stat.games_lost += 1
            mode_stat.current_streak = 0

        if self.mode == "classic":
            classic_prog = db.query(DBClassicProgress).filter(DBClassicProgress.user_id == self.user_id).first()
            if not classic_prog:
                classic_prog = DBClassicProgress(user_id=self.user_id)
                db.add(classic_prog)

            if won:
                classic_prog.consecutive_losses = 0
                classic_prog.xp += self.score
                if self.level == classic_prog.current_level and classic_prog.current_level < 100:
                    classic_prog.current_level += 1
                    if classic_prog.current_level > classic_prog.highest_level:
                        classic_prog.highest_level = classic_prog.current_level
            else:
                classic_prog.consecutive_losses += 1
                if classic_prog.consecutive_losses >= 5:
                    msg = random.choice(WITTY_LOSS_MESSAGES)
                    sug = f"Tip for '{self.secret_word.upper()}' ({self.word_data.get('part_of_speech', '')}): {self.word_data.get('definition', '')}"
                    self.witty_popup = WittyLossPopupPayload(
                        title="5-Loss Defeat Streak!",
                        message=msg,
                        consecutive_losses=classic_prog.consecutive_losses,
                        vocabulary_suggestion=sug
                    )

        if self.mode == "classic" and not won:
            heart_state = db.query(DBUserHeartState).filter(DBUserHeartState.user_id == self.user_id).first()
            if heart_state:
                heart_state.hearts_remaining = max(0, self.lives_remaining)
                heart_state.last_regen_timestamp = time.time()

        hints_cnt = sum([1 for c in [self.clue1_definition, self.clue2_sentence, self.clue3_context] if c is not None])
        history = DBGameHistory(
            user_id=self.user_id,
            mode=self.mode,
            level=self.level,
            category=self.word_data.get('category', 'General'),
            word=self.secret_word,
            won=won,
            score=self.score,
            mistakes=self.mistakes,
            hearts_remaining=self.lives_remaining,
            hints_used=hints_cnt,
            duration_seconds=int(time.time() - self.start_time)
        )
        db.add(history)
        db.commit()

    def to_response(self) -> GameStateResponse:
        k_card = None
        if self.status in ["won", "lost"]:
            k_card = KnowledgeCard(
                word=self.secret_word.upper(),
                definition=self.word_data.get('definition', 'N/A'),
                part_of_speech=self.word_data.get('part_of_speech', 'N/A'),
                synonyms=self.word_data.get('synonyms', []),
                category=self.word_data.get('category', 'General')
            )

        return GameStateResponse(
            game_id=self.game_id,
            mode=self.mode,
            level=self.level,
            tier_label=level_service.get_tier_label(self.level),
            masked_word=self.get_masked_word(),
            revealed_indices=list(self.revealed_indices),
            lives_remaining=self.lives_remaining,
            score=self.score,
            combo=self.combo,
            mistakes=self.mistakes,
            status=self.status,
            word_dna=self.get_word_dna(),
            guessed_letters=list(self.guessed_letters),
            clue1_definition=self.clue1_definition,
            clue2_sentence=self.clue2_sentence,
            clue3_context=self.clue3_context,
            knowledge_card=k_card,
            witty_loss_popup=self.witty_popup
        )

class GameEngine:
    def __init__(self):
        self.active_sessions: Dict[str, GameSession] = {}
        self.session_played_words: Dict[str, set] = {}

    def calculate_heart_regen(self, user_id: str, db: Session) -> tuple[int, int]:
        heart_state = db.query(DBUserHeartState).filter(DBUserHeartState.user_id == user_id).first()
        if not heart_state:
            return MAX_HEARTS, 0

        if heart_state.hearts_remaining >= MAX_HEARTS:
            return MAX_HEARTS, 0

        now = time.time()
        elapsed = now - heart_state.last_regen_timestamp
        hearts_to_add = int(elapsed // HEART_REGEN_INTERVAL_SECONDS)

        if hearts_to_add > 0:
            heart_state.hearts_remaining = min(MAX_HEARTS, heart_state.hearts_remaining + hearts_to_add)
            heart_state.last_regen_timestamp = now - (elapsed % HEART_REGEN_INTERVAL_SECONDS)
            db.commit()

        if heart_state.hearts_remaining >= MAX_HEARTS:
            seconds_left = 0
        else:
            seconds_left = int(HEART_REGEN_INTERVAL_SECONDS - (now - heart_state.last_regen_timestamp) % HEART_REGEN_INTERVAL_SECONDS)

        return heart_state.hearts_remaining, seconds_left

    def create_game(self, mode: str, level: int = 1, category: str = "General", user_id: Optional[str] = None, db: Optional[Session] = None) -> GameSession:
        game_id = str(uuid.uuid4())
        anon_key = user_id or "anon_guest"

        if anon_key not in self.session_played_words:
            self.session_played_words[anon_key] = set()

        played_set = set(self.session_played_words[anon_key])

        if db and user_id:
            try:
                hist_words = db.query(DBGameHistory.word).filter(DBGameHistory.user_id == user_id).all()
                codex_words = db.query(DBUserCodex.word).filter(DBUserCodex.user_id == user_id).all()
                for r in hist_words:
                    if r[0]: played_set.add(r[0].lower())
                for r in codex_words:
                    if r[0]: played_set.add(r[0].lower())
            except Exception:
                pass

        exclude_words = list(played_set)

        if mode == "classic":
            word_data = level_service.select_word_for_level(level=level, category=category, exclude_words=exclude_words)
        else:
            word_data = word_service.select_word(difficulty=2, category=category, exclude_words=exclude_words)

        # Record selected word in memory so it cannot repeat for this user/session
        if word_data and 'word' in word_data:
            self.session_played_words[anon_key].add(word_data['word'].lower())

        session = GameSession(game_id=game_id, mode=mode, word_data=word_data, level=level, user_id=user_id)
        
        if db and user_id and mode == "classic":
            hearts, _ = self.calculate_heart_regen(user_id, db)
            session.lives_remaining = hearts

        self.active_sessions[game_id] = session
        return session

    def create_daily_game(self, date_str: str, user_id: Optional[str] = None) -> GameSession:
        game_id = f"daily_{date_str}_{user_id or 'anon'}"
        word_data = word_service.get_daily_word(date_str)
        session = GameSession(game_id=game_id, mode="daily", word_data=word_data, level=1, user_id=user_id)
        self.active_sessions[game_id] = session
        return session

    def get_session(self, game_id: str) -> Optional[GameSession]:
        return self.active_sessions.get(game_id)

game_engine = GameEngine()
