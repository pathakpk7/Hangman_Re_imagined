from typing import Dict, Any, List, Optional
from backend.app.services.word_service import word_service

class ClassicLevelConfig:
    def __init__(self, level: int):
        self.level = max(1, min(100, level))
        
        if self.level <= 4:
            self.tier_label = "Very Easy"
            self.min_length = 3
            self.max_length = 5
            self.min_difficulty = 1
            self.max_difficulty = 1
            self.difficulty_score_min = 1.0
            self.difficulty_score_max = 2.2
        elif self.level <= 9:
            self.tier_label = "Easy"
            self.min_length = 4
            self.max_length = 6
            self.min_difficulty = 1
            self.max_difficulty = 2
            self.difficulty_score_min = 1.8
            self.difficulty_score_max = 2.8
        elif self.level <= 19:
            self.tier_label = "Easy / Intermediate"
            self.min_length = 5
            self.max_length = 7
            self.min_difficulty = 2
            self.max_difficulty = 2
            self.difficulty_score_min = 2.3
            self.difficulty_score_max = 3.3
        elif self.level <= 29:
            self.tier_label = "Intermediate"
            self.min_length = 6
            self.max_length = 8
            self.min_difficulty = 2
            self.max_difficulty = 3
            self.difficulty_score_min = 2.8
            self.difficulty_score_max = 3.8
        elif self.level <= 39:
            self.tier_label = "Intermediate / Challenging"
            self.min_length = 6
            self.max_length = 9
            self.min_difficulty = 3
            self.max_difficulty = 3
            self.difficulty_score_min = 3.3
            self.difficulty_score_max = 4.3
        elif self.level <= 49:
            self.tier_label = "Challenging"
            self.min_length = 7
            self.max_length = 10
            self.min_difficulty = 3
            self.max_difficulty = 4
            self.difficulty_score_min = 3.8
            self.difficulty_score_max = 4.8
        elif self.level <= 59:
            self.tier_label = "Hard"
            self.min_length = 8
            self.max_length = 11
            self.min_difficulty = 4
            self.max_difficulty = 4
            self.difficulty_score_min = 4.3
            self.difficulty_score_max = 5.3
        elif self.level <= 69:
            self.tier_label = "Hard+"
            self.min_length = 8
            self.max_length = 12
            self.min_difficulty = 4
            self.max_difficulty = 5
            self.difficulty_score_min = 4.8
            self.difficulty_score_max = 5.8
        elif self.level <= 79:
            self.tier_label = "Advanced"
            self.min_length = 9
            self.max_length = 13
            self.min_difficulty = 5
            self.max_difficulty = 5
            self.difficulty_score_min = 5.3
            self.difficulty_score_max = 6.5
        elif self.level <= 89:
            self.tier_label = "Expert"
            self.min_length = 10
            self.max_length = 14
            self.min_difficulty = 5
            self.max_difficulty = 5
            self.difficulty_score_min = 5.8
            self.difficulty_score_max = 7.5
        elif self.level <= 99:
            self.tier_label = "Very Expert"
            self.min_length = 11
            self.max_length = 16
            self.min_difficulty = 5
            self.max_difficulty = 5
            self.difficulty_score_min = 6.3
            self.difficulty_score_max = 8.5
        else:
            self.tier_label = "Hardcore Expert"
            self.min_length = 12
            self.max_length = 20
            self.min_difficulty = 5
            self.max_difficulty = 5
            self.difficulty_score_min = 7.0
            self.difficulty_score_max = 12.0

class LevelService:
    def get_level_config(self, level: int) -> ClassicLevelConfig:
        return ClassicLevelConfig(level)

    def get_difficulty_for_level(self, level: int) -> int:
        return self.get_level_config(level).difficulty_level if hasattr(self.get_level_config(level), 'difficulty_level') else self.get_level_config(level).min_difficulty

    def get_tier_label(self, level: int) -> str:
        return self.get_level_config(level).tier_label

    def select_word_for_level(self, level: int, category: str = "General", exclude_words: Optional[List[str]] = None) -> Dict[str, Any]:
        cfg = self.get_level_config(level)
        word_data = word_service.select_word_for_level_config(
            min_length=cfg.min_length,
            max_length=cfg.max_length,
            min_score=cfg.difficulty_score_min,
            max_score=cfg.difficulty_score_max,
            difficulty=cfg.min_difficulty,
            category=category,
            exclude_words=exclude_words
        )
        word_data["level"] = level
        word_data["tier_label"] = cfg.tier_label
        return word_data

level_service = LevelService()
