from typing import Dict, Any, List
from backend.app.services.word_service import word_service

class LevelService:
    def get_difficulty_for_level(self, level: int) -> int:
        """Map 100 levels to difficulty scaling (1 to 5)"""
        if level <= 15:
            return 1  # Very Easy
        elif level <= 30:
            return 2  # Easy
        elif level <= 50:
            return 3  # Moderate
        elif level <= 70:
            return 4  # Challenging
        elif level <= 85:
            return 4  # Hard
        elif level <= 95:
            return 5  # Expert
        else:
            return 5  # Hardcore Expert

    def get_tier_label(self, level: int) -> str:
        if level <= 15:
            return "Very Easy"
        elif level <= 30:
            return "Easy"
        elif level <= 50:
            return "Moderate"
        elif level <= 70:
            return "Challenging"
        elif level <= 85:
            return "Hard"
        elif level <= 95:
            return "Expert"
        else:
            return "Hardcore Expert"

    def select_word_for_level(self, level: int, category: str = "General", exclude_words: List[str] = None) -> Dict[str, Any]:
        diff = self.get_difficulty_for_level(level)
        word_data = word_service.select_word(difficulty=diff, category=category, exclude_words=exclude_words)
        word_data["level"] = level
        word_data["tier_label"] = self.get_tier_label(level)
        return word_data

level_service = LevelService()
