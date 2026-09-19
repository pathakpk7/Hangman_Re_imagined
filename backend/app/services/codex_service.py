from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models_db import DBUserCodex

class CodexService:
    def record_word_encounter(self, user_id: str, word_data: Dict[str, Any], won: bool, db: Session):
        if not user_id:
            return

        word_str = word_data.get('word', '').lower()
        if not word_str:
            return

        entry = db.query(DBUserCodex).filter(
            DBUserCodex.user_id == user_id,
            DBUserCodex.word == word_str
        ).first()

        syns_str = ", ".join(word_data.get('synonyms', [])) if isinstance(word_data.get('synonyms'), list) else str(word_data.get('synonyms', ''))

        if not entry:
            entry = DBUserCodex(
                user_id=user_id,
                word=word_str,
                category=word_data.get('category', 'General'),
                definition=word_data.get('definition', ''),
                part_of_speech=word_data.get('part_of_speech', 'noun'),
                example_sentence=word_data.get('example_sentence', ''),
                synonyms=syns_str,
                times_encountered=1,
                times_won=1 if won else 0,
                mastery_status="mastered" if won else "learning",
                last_encountered_at=datetime.now(timezone.utc)
            )
            db.add(entry)
        else:
            entry.times_encountered += 1
            if won:
                entry.times_won += 1
            if entry.times_won >= 2 or won:
                entry.mastery_status = "mastered"
            entry.last_encountered_at = datetime.now(timezone.utc)

        try:
            db.commit()
        except Exception:
            db.rollback()

    def get_user_codex(self, user_id: str, query: Optional[str], category: Optional[str], db: Session) -> Dict[str, Any]:
        q = db.query(DBUserCodex).filter(DBUserCodex.user_id == user_id)

        if category and category.lower() != 'all':
            q = q.filter(DBUserCodex.category.ilike(category))

        if query and query.strip():
            search_term = f"%{query.strip()}%"
            q = q.filter(
                (DBUserCodex.word.ilike(search_term)) | 
                (DBUserCodex.definition.ilike(search_term))
            )

        entries = q.order_by(DBUserCodex.last_encountered_at.desc()).all()

        total_unlocked = db.query(DBUserCodex).filter(DBUserCodex.user_id == user_id).count()
        total_mastered = db.query(DBUserCodex).filter(
            DBUserCodex.user_id == user_id,
            DBUserCodex.mastery_status == "mastered"
        ).count()

        items = []
        for e in entries:
            syn_list = [s.strip() for s in e.synonyms.split(',') if s.strip()] if e.synonyms else []
            items.append({
                "id": e.id,
                "word": e.word,
                "category": e.category,
                "definition": e.definition,
                "part_of_speech": e.part_of_speech,
                "example_sentence": e.example_sentence,
                "synonyms": syn_list,
                "times_encountered": e.times_encountered,
                "times_won": e.times_won,
                "mastery_status": e.mastery_status,
            })

        return {
            "total_unlocked": total_unlocked,
            "total_mastered": total_mastered,
            "items": items
        }

codex_service = CodexService()
