import sqlite3
import os
import random
import hashlib
import json
import re
from typing import Dict, Any, Optional, List
from backend.app.config import settings

PRESET_CATEGORIES = [
    "Technology", "Science", "Nature", "Animals", "Space", "Geography",
    "Food & Cooking", "Sports", "History", "Medicine", "Arts & Culture", "Business"
]

FALLBACK_WORDS = [
    # Technology (10)
    {
        "word": "code", "length": 4, "vowel_count": 2, "consonant_count": 2, "has_repeated_letters": False, "frequency": 4.8, "difficulty": 1, "part_of_speech": "noun",
        "definition": "Program instructions written by a programmer.",
        "example_sentence": "Engineers write clean ___ to build modern web applications.",
        "striking_clue": "Software developers write these text instructions to command a computer to perform tasks.",
        "synonyms": ["script", "program", "instructions"], "category": "Technology"
    },
    {
        "word": "data", "length": 4, "vowel_count": 2, "consonant_count": 2, "has_repeated_letters": True, "frequency": 4.9, "difficulty": 1, "part_of_speech": "noun",
        "definition": "Facts and statistics collected together for reference or analysis.",
        "example_sentence": "The server processed gigabytes of user ___ securely.",
        "striking_clue": "Digital systems gather and process these raw information records to produce analytical insights.",
        "synonyms": ["information", "records", "facts"], "category": "Technology"
    },
    {
        "word": "algorithm", "length": 9, "vowel_count": 3, "consonant_count": 6, "has_repeated_letters": False, "frequency": 4.5, "difficulty": 2, "part_of_speech": "noun",
        "definition": "A process or set of rules to be followed in calculations.",
        "example_sentence": "The computer executed an efficient ___ to sort millions of data points.",
        "striking_clue": "This step-by-step mathematical procedure directs a program to solve complex computational problems.",
        "synonyms": ["procedure", "formula", "routine"], "category": "Technology"
    },
    {
        "word": "hardware", "length": 8, "vowel_count": 3, "consonant_count": 5, "has_repeated_letters": True, "frequency": 4.3, "difficulty": 2, "part_of_speech": "noun",
        "definition": "The physical components of a computer system.",
        "example_sentence": "Upgrading the graphics ___ improved system performance dramatically.",
        "striking_clue": "This term refers to the tangible, physical circuitry and equipment inside a computer casing.",
        "synonyms": ["equipment", "machinery", "components"], "category": "Technology"
    },
    {
        "word": "encryption", "length": 10, "vowel_count": 4, "consonant_count": 6, "has_repeated_letters": True, "frequency": 3.8, "difficulty": 3, "part_of_speech": "noun",
        "definition": "The process of encoding data to prevent unauthorized access.",
        "example_sentence": "End-to-end ___ secures message transmission between users.",
        "striking_clue": "Security protocols use this mathematical encoding process to keep private messages secret from eavesdroppers.",
        "synonyms": ["encoding", "ciphering", "protection"], "category": "Technology"
    },
    {
        "word": "microprocessor", "length": 14, "vowel_count": 5, "consonant_count": 9, "has_repeated_letters": True, "frequency": 3.2, "difficulty": 4, "part_of_speech": "noun",
        "definition": "An integrated circuit that contains all the functions of a CPU.",
        "example_sentence": "The multi-core ___ executes billions of cycles per second.",
        "striking_clue": "This miniature silicon chip acts as the central brain of a computer executing instructions.",
        "synonyms": ["chip", "cpu", "processor"], "category": "Technology"
    },
    {
        "word": "cybernetics", "length": 11, "vowel_count": 4, "consonant_count": 7, "has_repeated_letters": True, "frequency": 3.0, "difficulty": 4, "part_of_speech": "noun",
        "definition": "The science of communications and automatic control systems.",
        "example_sentence": "Advanced ___ bridges human biology with mechanical prosthetics.",
        "striking_clue": "This interdisciplinary field studies feedback loops connecting living organisms and automatic machinery.",
        "synonyms": ["automation", "robotics", "bionics"], "category": "Technology"
    },
    {
        "word": "cryptography", "length": 12, "vowel_count": 3, "consonant_count": 9, "has_repeated_letters": True, "frequency": 3.1, "difficulty": 5, "part_of_speech": "noun",
        "definition": "The practice of securing communication in the presence of adversaries.",
        "example_sentence": "Quantum-resistant ___ protects sensitive financial ledgers.",
        "striking_clue": "This science of secret writing creates mathematical ciphers to safeguard sensitive data transfers.",
        "synonyms": ["ciphers", "steganography", "secret writing"], "category": "Technology"
    },
    {
        "word": "supercomputer", "length": 13, "vowel_count": 5, "consonant_count": 8, "has_repeated_letters": True, "frequency": 3.5, "difficulty": 5, "part_of_speech": "noun",
        "definition": "A high-performance computer capable of processing complex calculations.",
        "example_sentence": "Scientists used a weather-modeling ___ to predict hurricane trajectories.",
        "striking_clue": "An extremely powerful computing facility designed to run massive scientific simulations at high speed.",
        "synonyms": ["mainframe", "supernode"], "category": "Technology"
    },
    {
        "word": "bandwidth", "length": 9, "vowel_count": 2, "consonant_count": 7, "has_repeated_letters": True, "frequency": 4.1, "difficulty": 3, "part_of_speech": "noun",
        "definition": "The maximum data transfer rate of a network connection.",
        "example_sentence": "High fiber-optic ___ enables smooth ultra-high-definition streaming.",
        "striking_clue": "Network speed performance depends on this maximum capacity measurement for transmitting data per second.",
        "synonyms": ["capacity", "throughput"], "category": "Technology"
    },

    # Science (10)
    {
        "word": "atom", "length": 4, "vowel_count": 2, "consonant_count": 2, "has_repeated_letters": False, "frequency": 4.7, "difficulty": 1, "part_of_speech": "noun",
        "definition": "The basic unit of a chemical element.",
        "example_sentence": "Protons and neutrons form the central nucleus of an ___.",
        "striking_clue": "This fundamental microscopic particle consists of a central nucleus surrounded by orbiting electrons.",
        "synonyms": ["particle", "unit", "element"], "category": "Science"
    },
    {
        "word": "cell", "length": 4, "vowel_count": 1, "consonant_count": 3, "has_repeated_letters": True, "frequency": 4.9, "difficulty": 1, "part_of_speech": "noun",
        "definition": "The smallest structural and functional unit of an organism.",
        "example_sentence": "The microscopic biological ___ is the basic building block of life.",
        "striking_clue": "Biologists regard this microscopic membrane-bound structure as the foundational building block of life.",
        "synonyms": ["unit", "corpuscle"], "category": "Science"
    },
    {
        "word": "electron", "length": 8, "vowel_count": 3, "consonant_count": 5, "has_repeated_letters": True, "frequency": 4.2, "difficulty": 2, "part_of_speech": "noun",
        "definition": "A stable subatomic particle with a charge of negative electricity.",
        "example_sentence": "An ___ orbits the positive atomic nucleus in distinct shells.",
        "striking_clue": "This negatively charged subatomic particle orbits around the positive center of an atomic nucleus.",
        "synonyms": ["lepton", "particle"], "category": "Science"
    },
    {
        "word": "molecule", "length": 8, "vowel_count": 4, "consonant_count": 4, "has_repeated_letters": True, "frequency": 4.1, "difficulty": 2, "part_of_speech": "noun",
        "definition": "A group of atoms bonded together representing the smallest unit of a compound.",
        "example_sentence": "A water ___ consists of two hydrogen atoms bonded to oxygen.",
        "striking_clue": "Two or more atoms form chemical bonds together to create this stable neutral unit of matter.",
        "synonyms": ["compound", "particle"], "category": "Science"
    },
    {
        "word": "photosynthesis", "length": 14, "vowel_count": 5, "consonant_count": 9, "has_repeated_letters": True, "frequency": 3.4, "difficulty": 3, "part_of_speech": "noun",
        "definition": "The biological process by which green plants convert light into chemical energy.",
        "example_sentence": "Plants use sunlight to perform ___ and produce oxygen.",
        "striking_clue": "Green plants utilize sunlight absorbed by chlorophyll to convert water and carbon dioxide into oxygen.",
        "synonyms": ["energy synthesis", "chlorophyll process"], "category": "Science"
    },
    {
        "word": "thermodynamics", "length": 14, "vowel_count": 4, "consonant_count": 10, "has_repeated_letters": True, "frequency": 3.1, "difficulty": 4, "part_of_speech": "noun",
        "definition": "The branch of physical science dealing with heat and temperature relations.",
        "example_sentence": "The second law of ___ states that entropy in an isolated system increases.",
        "striking_clue": "This branch of physics investigates how heat, work, entropy, and energy transform across thermal systems.",
        "synonyms": ["heat physics", "energy dynamics"], "category": "Science"
    },
    {
        "word": "quantum", "length": 7, "vowel_count": 3, "consonant_count": 4, "has_repeated_letters": True, "frequency": 3.9, "difficulty": 3, "part_of_speech": "noun",
        "definition": "A discrete quantity of energy proportional in magnitude to the frequency of radiation.",
        "example_sentence": "Physicists explored subatomic particle interactions using ___ mechanics.",
        "striking_clue": "This physics term describes the smallest discrete unit of energy involved in subatomic interactions.",
        "synonyms": ["unit", "quanta"], "category": "Science"
    },
    {
        "word": "biotechnology", "length": 13, "vowel_count": 5, "consonant_count": 8, "has_repeated_letters": True, "frequency": 3.3, "difficulty": 4, "part_of_speech": "noun",
        "definition": "The exploitation of biological processes for industrial and scientific purposes.",
        "example_sentence": "Modern agricultural ___ engineered drought-resistant crops.",
        "striking_clue": "Scientists apply genetic manipulation and cellular organisms to engineer new medicines and crops.",
        "synonyms": ["bioengineering", "genetic technology"], "category": "Science"
    },
    {
        "word": "crystallography", "length": 15, "vowel_count": 4, "consonant_count": 11, "has_repeated_letters": True, "frequency": 2.8, "difficulty": 5, "part_of_speech": "noun",
        "definition": "The branch of science concerned with the structure and properties of crystals.",
        "example_sentence": "X-ray ___ revealed the double-helix geometry of DNA.",
        "striking_clue": "Researchers shoot X-ray beams through solid minerals to map atomic arrangement in three dimensions.",
        "synonyms": ["crystal analysis", "x-ray diffraction"], "category": "Science"
    },
    {
        "word": "electromagnetism", "length": 16, "vowel_count": 5, "consonant_count": 11, "has_repeated_letters": True, "frequency": 2.9, "difficulty": 5, "part_of_speech": "noun",
        "definition": "The interaction of electric currents or fields and magnetic fields.",
        "example_sentence": "Maxwell unified electricity and magnetism into classic ___ theory.",
        "striking_clue": "This fundamental physical force governs interactions between electrically charged particles and magnetic fields.",
        "synonyms": ["magnetic field theory", "electrodynamics"], "category": "Science"
    },

    # Nature (10)
    {
        "word": "leaf", "length": 4, "vowel_count": 2, "consonant_count": 2, "has_repeated_letters": False, "frequency": 4.8, "difficulty": 1, "part_of_speech": "noun",
        "definition": "A flattened structure of a higher plant, typically green and blade-like.",
        "example_sentence": "A green ___ absorbs sunlight to synthesize plant nutrients.",
        "striking_clue": "This flat green foliage structure sprouts from plant stems to catch sunlight for food production.",
        "synonyms": ["frond", "blade", "foliage"], "category": "Nature"
    },
    {
        "word": "tree", "length": 4, "vowel_count": 2, "consonant_count": 2, "has_repeated_letters": True, "frequency": 5.0, "difficulty": 1, "part_of_speech": "noun",
        "definition": "A woody perennial plant, typically having a single stem or trunk.",
        "example_sentence": "The ancient oak ___ provided shade over the grassy meadow.",
        "striking_clue": "A tall perennial plant supported by a sturdy wooden trunk with spreading branches and foliage.",
        "synonyms": ["sapling", "timber"], "category": "Nature"
    },
    {
        "word": "forest", "length": 6, "vowel_count": 2, "consonant_count": 4, "has_repeated_letters": False, "frequency": 4.6, "difficulty": 2, "part_of_speech": "noun",
        "definition": "A large area covered chiefly with trees and undergrowth.",
        "example_sentence": "Dense pine trees stretched across the mountain ___.",
        "striking_clue": "An expansive natural ecosystem covered densely with trees, underbrush, and diverse woodland wildlife.",
        "synonyms": ["woods", "jungle", "woodland"], "category": "Nature"
    },
    {
        "word": "glacier", "length": 7, "vowel_count": 3, "consonant_count": 4, "has_repeated_letters": False, "frequency": 3.8, "difficulty": 2, "part_of_speech": "noun",
        "definition": "A slowly moving mass or river of ice formed by the accumulation of snow.",
        "example_sentence": "The massive alpine ___ carved a deep valley over millennia.",
        "striking_clue": "This colossal river of accumulated ice creeps slowly down mountain slopes, carving out deep valleys.",
        "synonyms": ["ice sheet", "icefield"], "category": "Nature"
    },
    {
        "word": "biodiversity", "length": 12, "vowel_count": 6, "consonant_count": 6, "has_repeated_letters": True, "frequency": 3.5, "difficulty": 3, "part_of_speech": "noun",
        "definition": "The variety of plant and animal life in a particular habitat.",
        "example_sentence": "The tropical rainforest possesses incredible biological ___.",
        "striking_clue": "Ecologists measure environmental health by looking at this rich variety of living species in a habitat.",
        "synonyms": ["ecosystem variety", "nature richness"], "category": "Nature"
    },
    {
        "word": "avalanche", "length": 9, "vowel_count": 4, "consonant_count": 5, "has_repeated_letters": True, "frequency": 3.6, "difficulty": 3, "part_of_speech": "noun",
        "definition": "A mass of snow, ice, and rocks falling rapidly down a mountainside.",
        "example_sentence": "Warnings were issued after a sudden snow ___ blocked the pass.",
        "striking_clue": "Skier safety alerts warn of this dangerous rapid slide of snow, ice, and rock rushing down a steep peak.",
        "synonyms": ["snowslide", "landslide"], "category": "Nature"
    },
    {
        "word": "precipitation", "length": 13, "vowel_count": 6, "consonant_count": 7, "has_repeated_letters": True, "frequency": 3.3, "difficulty": 4, "part_of_speech": "noun",
        "definition": "Rain, snow, sleet, or hail that falls to the ground.",
        "example_sentence": "Heavy seasonal ___ restored water levels in coastal reservoirs.",
        "striking_clue": "Meteorologists use this collective term for any form of condensed water falling from atmospheric clouds.",
        "synonyms": ["rainfall", "downpour", "sleet"], "category": "Nature"
    },
    {
        "word": "deforestation", "length": 13, "vowel_count": 6, "consonant_count": 7, "has_repeated_letters": True, "frequency": 3.2, "difficulty": 4, "part_of_speech": "noun",
        "definition": "The action of clearing a wide area of trees.",
        "example_sentence": "Environmental policies aim to combat illegal forest ___.",
        "striking_clue": "Conservation efforts combat this destructive practice of clearing wide tracts of forest trees for land development.",
        "synonyms": ["logging", "clearance"], "category": "Nature"
    },

    # Animals (10)
    {
        "word": "lion", "length": 4, "vowel_count": 2, "consonant_count": 2, "has_repeated_letters": False, "frequency": 4.8, "difficulty": 1, "part_of_speech": "noun",
        "definition": "A large wild cat of the genus Panthera native to Africa and India.",
        "example_sentence": "The male ___ let out a loud roar across the savanna.",
        "striking_clue": "This majestic African feline apex predator is widely referred to as the king of the savanna.",
        "synonyms": ["feline", "predator"], "category": "Animals"
    },
    {
        "word": "bear", "length": 4, "vowel_count": 2, "consonant_count": 2, "has_repeated_letters": False, "frequency": 4.9, "difficulty": 1, "part_of_speech": "noun",
        "definition": "A large heavy mammal with thick fur and a short tail.",
        "example_sentence": "A grizzly ___ fished for salmon in the clear river stream.",
        "striking_clue": "A heavy furry mammal known for hibernating during winter months and catching river salmon.",
        "synonyms": ["grizzly", "beast"], "category": "Animals"
    },
    {
        "word": "chameleon", "length": 9, "vowel_count": 4, "consonant_count": 5, "has_repeated_letters": True, "frequency": 3.7, "difficulty": 2, "part_of_speech": "noun",
        "definition": "A reptile known for changing color to blend into its environment.",
        "example_sentence": "The small ___ blended seamlessly into the tree branch.",
        "striking_clue": "This slow-moving specialized lizard changes skin pigmentation to blend into surrounding foliage.",
        "synonyms": ["lizard", "adapter"], "category": "Animals"
    },
    {
        "word": "flamingo", "length": 8, "vowel_count": 3, "consonant_count": 5, "has_repeated_letters": False, "frequency": 3.8, "difficulty": 2, "part_of_speech": "noun",
        "definition": "A tall wading bird with bright pink feathers and long legs.",
        "example_sentence": "A flock of pink ___ stood gracefully in shallow lake waters.",
        "striking_clue": "This striking wading bird is famous for its bright pink plumage and standing on one long leg.",
        "synonyms": ["wader", "pink bird"], "category": "Animals"
    },

    # Space (10)
    {
        "word": "star", "length": 4, "vowel_count": 1, "consonant_count": 3, "has_repeated_letters": False, "frequency": 5.1, "difficulty": 1, "part_of_speech": "noun",
        "definition": "A luminous point in the night sky that is a large, remote incandescent body.",
        "example_sentence": "A bright evening ___ shone clearly above the horizon.",
        "striking_clue": "A massive sphere of burning plasma generating heat and light via nuclear fusion in deep space.",
        "synonyms": ["sun", "sunlet", "luminary"], "category": "Space"
    },
    {
        "word": "moon", "length": 4, "vowel_count": 2, "consonant_count": 2, "has_repeated_letters": True, "frequency": 5.0, "difficulty": 1, "part_of_speech": "noun",
        "definition": "The natural satellite of the earth, visible by reflected light from the sun.",
        "example_sentence": "The full ___ illuminated the quiet countryside at midnight.",
        "striking_clue": "This natural rocky satellite orbits Earth, controlling ocean tides and shining at night.",
        "synonyms": ["satellite", "lunar body"], "category": "Space"
    },
    {
        "word": "astronomy", "length": 9, "vowel_count": 3, "consonant_count": 6, "has_repeated_letters": True, "frequency": 4.0, "difficulty": 2, "part_of_speech": "noun",
        "definition": "The scientific study of stars, planets, galaxies, and celestial bodies.",
        "example_sentence": "She studied ___ through a powerful mountain telescope.",
        "striking_clue": "Stargazers and scientists practice this branch of science to study celestial bodies, planets, and galaxies.",
        "synonyms": ["stargazing", "astrophysics"], "category": "Space"
    },
    {
        "word": "astronaut", "length": 9, "vowel_count": 4, "consonant_count": 5, "has_repeated_letters": False, "frequency": 3.8, "difficulty": 3, "part_of_speech": "noun",
        "definition": "A person trained to travel in a spacecraft.",
        "example_sentence": "The ___ conducted a spacewalk outside the international space station.",
        "striking_clue": "This is the person who leaves Earth to work beyond its atmosphere in space missions.",
        "synonyms": ["cosmonaut", "space traveler"], "category": "Space"
    },
    {
        "word": "thermometer", "length": 11, "vowel_count": 4, "consonant_count": 7, "has_repeated_letters": True, "frequency": 3.6, "difficulty": 3, "part_of_speech": "noun",
        "definition": "An instrument for measuring and indicating temperature.",
        "example_sentence": "The nurse checked the clinical ___ to measure fever level.",
        "striking_clue": "You would use this instrument to find out whether something is hot, cold, or somewhere in between.",
        "synonyms": ["temperature gauge", "heat sensor"], "category": "Medicine"
    },
    {
        "word": "archaeologist", "length": 13, "vowel_count": 6, "consonant_count": 7, "has_repeated_letters": True, "frequency": 3.2, "difficulty": 4, "part_of_speech": "noun",
        "definition": "A person who studies human history by excavating sites and analyzing artifacts.",
        "example_sentence": "The ___ uncovered ancient pottery shards buried beneath desert sands.",
        "striking_clue": "This person studies evidence left behind by civilizations that existed long ago by excavating ancient sites.",
        "synonyms": ["excavator", "antiquarian"], "category": "History"
    }
]

class WordService:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.DATABASE_PATH

    def _get_connection(self):
        if os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        return None

    def _map_category(self, category: str) -> List[str]:
        if not category or category == "General":
            return []
        cat_map = {
            "Food & Cooking": ["Food & Cooking", "Food", "Cooking"],
            "Arts & Culture": ["Arts & Culture", "Arts", "Culture", "Art"],
            "Technology": ["Technology", "Tech"],
            "Science": ["Science"],
            "Nature": ["Nature"],
            "Animals": ["Animals", "Animal"],
            "Space": ["Space", "Astronomy"],
            "Geography": ["Geography"],
            "Sports": ["Sports", "Sport"],
            "History": ["History"],
            "Medicine": ["Medicine", "Medical"],
            "Business": ["Business", "Finance", "Commerce"]
        }
        return cat_map.get(category, [category])

    def calculate_difficulty_score(self, word: str, freq: float, length: int, cons_cnt: int, vow_cnt: int, has_repeated: bool, category: str) -> float:
        """Multi-factor difficulty calculation algorithm returning score from 1.0 to 10.0+"""
        length_factor = length * 0.45
        freq_factor = max(0.0, (7.0 - freq) * 0.6)
        
        rare_letter_cnt = sum(1 for c in word.lower() if c in 'jkqxz')
        rare_letter_factor = rare_letter_cnt * 0.75
        
        repeated_factor = 0.4 if has_repeated else 0.0
        consonant_imbalance = 0.5 if cons_cnt > (vow_cnt * 2) else 0.0
        
        complex_categories = ['Medicine', 'Business', 'Philosophy', 'Literature', 'Engineering', 'Computing']
        category_factor = 0.6 if category in complex_categories else 0.0
        
        score = length_factor + freq_factor + rare_letter_factor + repeated_factor + consonant_imbalance + category_factor
        return round(max(1.0, score), 2)

    def sanitize_definition(self, raw_def: str) -> str:
        if not raw_def:
            return "A fundamental vocabulary concept."
        clean = re.sub(r'\(\d{4}-\d{4}\)', '', raw_def)
        clean = re.sub(r'\s+', ' ', clean).strip()
        if clean.endswith('.'):
            clean = clean[:-1]
        if clean:
            clean = clean[0].upper() + clean[1:]
        return clean

    def infer_origin(self, word: str, category: str) -> str:
        w_lower = word.lower()
        if any(w_lower.endswith(suf) for suf in ['logy', 'graphy', 'metry', 'nomy', 'phobia', 'cracy']):
            return "Classical Greek origin"
        if any(w_lower.endswith(suf) for suf in ['tion', 'sion', 'ment', 'able', 'ible', 'ance', 'ence']):
            return "Latin / Old French origin"
        if any(w_lower.endswith(suf) for suf in ['ism', 'ist', 'ic', 'ize', 'ise']):
            return "Greek / Latin origin"
        if category in ['Technology', 'Computing', 'Tech']:
            return "Modern Technical / English"
        if category in ['Science', 'Medicine', 'Nature']:
            return "Latin / Scientific terminology"
        return "Old English / Latin root"

    def infer_usage_context(self, word: str, definition: str, category: str, part_of_speech: str) -> str:
        clean_def = self.sanitize_definition(definition)
        if clean_def and clean_def[0].isupper():
            clean_def = clean_def[0].lower() + clean_def[1:]
        
        pos = part_of_speech.lower() if part_of_speech else 'noun'
        cat = category if category else 'General'

        if pos == 'noun':
            return f"Commonly applied in {cat} when identifying {clean_def}."
        elif pos == 'verb':
            return f"Used in {cat} to denote the action of {clean_def}."
        elif pos == 'adjective':
            return f"Used in {cat} to describe something that is {clean_def}."
        return f"Used in {cat} applications relating to {clean_def}."

    def generate_legitimate_sentence(self, word: str, definition: str, category: str, part_of_speech: str) -> str:
        pos = (part_of_speech or 'noun').lower()
        cat = (category or 'General').lower()
        word_str = word.lower()

        clean_def = self.sanitize_definition(definition)
        
        if pos == 'noun':
            sentence = f"In {cat}, the team analyzed the ___ to ensure accurate system operations."
        elif pos == 'verb':
            sentence = f"Engineers often need to ___ the system parameters before deployment."
        elif pos == 'adjective':
            sentence = f"The research committee described the observed results as ___."
        else:
            sentence = f"The specialist consulted the ___ during the technical evaluation."

        pattern = re.compile(re.escape(word_str), re.IGNORECASE)
        return pattern.sub("___", sentence)

    def generate_striking_clue(self, word: str, definition: str, part_of_speech: str, category: str) -> str:
        """Transforms dictionary definition into a concise 1-sentence striking clue without target word spoilers"""
        word_str = word.lower()
        def_clean = self.sanitize_definition(definition)

        pos_str = (part_of_speech or 'noun').lower()
        if pos_str == 'noun':
            if def_clean.lower().startswith(('a ', 'an ', 'the ')):
                clue = f"This is {def_clean[0].lower() + def_clean[1:]}."
            else:
                clue = f"This refers to {def_clean[0].lower() + def_clean[1:]}."
        elif pos_str == 'verb':
            clue = f"To perform the action of {def_clean[0].lower() + def_clean[1:]}."
        elif pos_str == 'adjective':
            clue = f"Describing something that is {def_clean[0].lower() + def_clean[1:]}."
        else:
            clue = f"A term in {category} meaning {def_clean[0].lower() + def_clean[1:]}."

        pattern = re.compile(re.escape(word_str), re.IGNORECASE)
        clue = pattern.sub("this concept", clue)
        clue = clue.split('.')[0] + '.'
        return clue

    def _format_word(self, w: Dict[str, Any]) -> Dict[str, Any]:
        w = dict(w)
        w['synonyms'] = json.loads(w['synonyms']) if isinstance(w.get('synonyms'), str) else (w.get('synonyms') or [])
        w['has_repeated_letters'] = bool(w.get('has_repeated_letters', False))
        
        word_str = w['word'].lower()
        raw_def = w.get('definition', 'A term in vocabulary.')
        w['definition'] = self.sanitize_definition(raw_def)

        pos_str = w.get('part_of_speech', 'noun')
        cat_str = w.get('category', 'General')

        if not w.get('origin'):
            w['origin'] = self.infer_origin(word_str, cat_str)

        if not w.get('usage_context'):
            w['usage_context'] = self.infer_usage_context(word_str, w['definition'], cat_str, pos_str)

        ex_sent = w.get('example_sentence')
        if not ex_sent or "In Technology, the concept of ___ is defined as:" in ex_sent or "In context, the term ___" in ex_sent:
            ex_sent = self.generate_legitimate_sentence(word_str, w['definition'], cat_str, pos_str)
        
        pattern = re.compile(re.escape(word_str), re.IGNORECASE)
        w['example_sentence'] = pattern.sub("___", ex_sent)

        # Generate striking clue if missing
        if not w.get('striking_clue'):
            w['striking_clue'] = self.generate_striking_clue(
                w['word'],
                w['definition'],
                pos_str,
                cat_str
            )
        else:
            w['striking_clue'] = pattern.sub("this concept", w['striking_clue'])

        # Calculate difficulty score if missing
        freq = float(w.get('frequency', 4.0))
        length = int(w.get('length', len(word_str)))
        cons_cnt = int(w.get('consonant_count', length // 2))
        vow_cnt = int(w.get('vowel_count', length - cons_cnt))
        has_rep = bool(w.get('has_repeated_letters', False))
        cat = w.get('category', 'General')

        w['difficulty_score'] = self.calculate_difficulty_score(word_str, freq, length, cons_cnt, vow_cnt, has_rep, cat)
        return w

    def get_word_by_id(self, word_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        if not conn:
            return next((w for w in FALLBACK_WORDS if w.get('id') == word_id), self._format_word(FALLBACK_WORDS[0]))
        
        cur = conn.cursor()
        cur.execute("SELECT * FROM words WHERE id = ?", (word_id,))
        row = cur.fetchone()
        conn.close()
        
        if row:
            return self._format_word(dict(row))
        return None

    def select_word_for_level_config(
        self,
        min_length: int = 3,
        max_length: int = 6,
        min_score: float = 1.0,
        max_score: float = 3.0,
        difficulty: int = 1,
        category: str = "General",
        exclude_words: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        exclude_words = [w.lower() for w in (exclude_words or [])]
        conn = self._get_connection()
        categories = self._map_category(category)

        if not conn:
            candidates = [
                w for w in FALLBACK_WORDS 
                if w['word'].lower() not in exclude_words 
                and min_length <= w['length'] <= max_length
            ]
            if not candidates:
                candidates = [w for w in FALLBACK_WORDS if w['word'].lower() not in exclude_words]
            if not candidates:
                candidates = FALLBACK_WORDS

            selected = random.choice(candidates)
            return self._format_word(selected)

        cur = conn.cursor()
        
        query = "SELECT * FROM words WHERE length >= ? AND length <= ?"
        params: List[Any] = [min_length, max_length]

        if categories:
            placeholders = ",".join("?" for _ in categories)
            query += f" AND category IN ({placeholders})"
            params.extend(categories)

        if exclude_words:
            ex_placeholders = ",".join("?" for _ in exclude_words)
            query += f" AND LOWER(word) NOT IN ({ex_placeholders})"
            params.extend(exclude_words)

        query += " ORDER BY RANDOM() LIMIT 20"
        
        try:
            cur.execute(query, params)
            rows = cur.fetchall()
            if rows:
                formatted_rows = [self._format_word(dict(r)) for r in rows]
                # Filter by difficulty_score range if possible
                matched = [w for w in formatted_rows if min_score <= w['difficulty_score'] <= max_score]
                if matched:
                    conn.close()
                    return random.choice(matched)
                conn.close()
                return random.choice(formatted_rows)
        except Exception:
            pass

        # Fallback to standard selection
        conn.close()
        return self.select_word(difficulty=difficulty, category=category, exclude_words=exclude_words)

    def select_word(self, difficulty: int = 2, category: str = "General", exclude_words: Optional[List[str]] = None) -> Dict[str, Any]:
        exclude_words = [w.lower() for w in (exclude_words or [])]
        conn = self._get_connection()
        categories = self._map_category(category)

        if not conn:
            candidates = [w for w in FALLBACK_WORDS if w['word'].lower() not in exclude_words]
            if not candidates:
                candidates = FALLBACK_WORDS

            if categories:
                cat_candidates = [w for w in candidates if w.get('category') in categories]
                if cat_candidates:
                    candidates = cat_candidates

            selected = random.choice(candidates)
            return self._format_word(selected)

        cur = conn.cursor()
        queries_to_try = []

        if difficulty and categories:
            cat_placeholders = ",".join("?" for _ in categories)
            queries_to_try.append((
                f"WHERE difficulty = ? AND category IN ({cat_placeholders})",
                [difficulty] + categories
            ))

        if categories:
            cat_placeholders = ",".join("?" for _ in categories)
            queries_to_try.append((
                f"WHERE category IN ({cat_placeholders})",
                categories
            ))

        if difficulty:
            queries_to_try.append((
                "WHERE difficulty = ?",
                [difficulty]
            ))

        queries_to_try.append(("", []))

        for where_clause, params in queries_to_try:
            sql = f"SELECT * FROM words {where_clause}"
            query_params = list(params)

            if exclude_words:
                ex_placeholders = ",".join("?" for _ in exclude_words)
                prefix = " AND " if where_clause else "WHERE "
                sql += f"{prefix}LOWER(word) NOT IN ({ex_placeholders})"
                query_params.extend(exclude_words)

            sql += " ORDER BY RANDOM() LIMIT 1"
            
            try:
                cur.execute(sql, query_params)
                row = cur.fetchone()
                if row:
                    conn.close()
                    return self._format_word(dict(row))
            except Exception:
                continue

        cur.execute("SELECT * FROM words ORDER BY RANDOM() LIMIT 1")
        row = cur.fetchone()
        conn.close()

        if row:
            return self._format_word(dict(row))

        return self._format_word(random.choice(FALLBACK_WORDS))

    def get_daily_word(self, date_str: str) -> Dict[str, Any]:
        conn = self._get_connection()
        if not conn:
            idx = int(hashlib.md5(date_str.encode()).hexdigest(), 16) % len(FALLBACK_WORDS)
            return self._format_word(FALLBACK_WORDS[idx])

        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM words")
        total = cur.fetchone()[0]
        
        if total == 0:
            return self._format_word(random.choice(FALLBACK_WORDS))

        hash_val = int(hashlib.sha256(date_str.encode('utf-8')).hexdigest(), 16)
        target_offset = hash_val % total

        cur.execute("SELECT * FROM words LIMIT 1 OFFSET ?", (target_offset,))
        row = cur.fetchone()
        conn.close()

        if row:
            return self._format_word(dict(row))

        return self._format_word(FALLBACK_WORDS[0])

    def get_categories(self) -> List[str]:
        return PRESET_CATEGORIES

word_service = WordService()
