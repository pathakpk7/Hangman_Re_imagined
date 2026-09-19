import sqlite3
import json
import os
import re
import math
import sys
import nltk

# Ensure required NLTK datasets are downloaded
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')
try:
    nltk.data.find('corpora/words')
except LookupError:
    nltk.download('words')

from nltk.corpus import wordnet as wn
from nltk.corpus import words as nltk_words

try:
    from wordfreq import word_frequency, zipf_frequency
    HAS_WORDFREQ = True
except ImportError:
    HAS_WORDFREQ = False

VOWELS = set('aeiou')

CATEGORY_KEYWORDS = {
    'Animals': ['animal', 'beast', 'mammal', 'bird', 'fish', 'reptile', 'insect', 'pet', 'wildlife', 'creature', 'dog', 'cat', 'lion', 'tiger', 'bear', 'elephant'],
    'Science': ['science', 'physics', 'chemistry', 'biology', 'experiment', 'atom', 'molecule', 'energy', 'force', 'element', 'theory', 'laboratory', 'cell', 'organism'],
    'Technology': ['technology', 'computer', 'software', 'network', 'digital', 'data', 'robot', 'code', 'internet', 'device', 'algorithm', 'system', 'cyber'],
    'Food': ['food', 'fruit', 'vegetable', 'dish', 'drink', 'meal', 'cuisine', 'bread', 'meat', 'sweet', 'spice', 'flavor', 'ingredient', 'cook'],
    'Sports': ['sport', 'game', 'player', 'team', 'ball', 'race', 'match', 'competition', 'score', 'stadium', 'athlete', 'fitness', 'exercise'],
    'Space': ['space', 'star', 'planet', 'galaxy', 'orbit', 'sun', 'moon', 'cosmos', 'asteroid', 'comet', 'universe', 'rocket', 'satellite', 'astronomy'],
    'Nature': ['nature', 'tree', 'flower', 'forest', 'river', 'mountain', 'ocean', 'plant', 'weather', 'climate', 'landscape', 'earth', 'season'],
    'Medicine': ['medicine', 'doctor', 'health', 'disease', 'hospital', 'treatment', 'drug', 'patient', 'therapy', 'virus', 'body', 'organ', 'symptom'],
    'Geography': ['geography', 'country', 'city', 'island', 'continent', 'map', 'capital', 'region', 'desert', 'valley', 'mountain', 'ocean', 'nation']
}

def get_wordnet_info(word):
    synsets = wn.synsets(word)
    if not synsets:
        return None
    
    primary_syn = synsets[0]
    definition = primary_syn.definition()
    
    pos_map = {
        'n': 'noun',
        'v': 'verb',
        'a': 'adjective',
        's': 'adjective',
        'r': 'adverb'
    }
    pos = pos_map.get(primary_syn.pos(), 'noun')
    
    synonyms = set()
    for syn in synsets[:3]:
        for lemma in syn.lemmas():
            name = lemma.name().replace('_', ' ')
            if name.lower() != word.lower() and name.isalpha():
                synonyms.add(name.lower())
    
    # Category detection based on hypernyms/definition
    matched_category = 'General'
    def_lower = definition.lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in def_lower for kw in keywords):
            matched_category = cat
            break

    return {
        'definition': definition.capitalize(),
        'pos': pos,
        'synonyms': list(synonyms)[:5],
        'category': matched_category
    }

def calculate_difficulty(word, freq_rank):
    length = len(word)
    unique_ratio = len(set(word)) / length
    infrequent_letters = sum(1 for c in word if c in 'jkqxz')
    
    # 1 (Easy) to 5 (Master)
    score = 0
    if length <= 5:
        score += 1
    elif length <= 8:
        score += 2
    elif length <= 11:
        score += 3
    else:
        score += 4

    if freq_rank < 3.0:
        score += 2
    elif freq_rank < 4.5:
        score += 1

    if infrequent_letters > 0:
        score += 1

    if unique_ratio > 0.8:
        score += 1

    return min(5, max(1, math.ceil(score / 1.6)))

def process_word_corpus(output_db_path, seed_sql_path):
    print("Starting word corpus preprocessing...")
    
    os.makedirs(os.path.dirname(output_db_path), exist_ok=True)
    os.makedirs(os.path.dirname(seed_sql_path), exist_ok=True)

    if os.path.exists(output_db_path):
        os.remove(output_db_path)

    conn = sqlite3.connect(output_db_path)
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT UNIQUE NOT NULL,
            length INTEGER NOT NULL,
            vowel_count INTEGER NOT NULL,
            consonant_count INTEGER NOT NULL,
            has_repeated_letters BOOLEAN NOT NULL,
            frequency REAL NOT NULL,
            difficulty INTEGER NOT NULL,
            part_of_speech TEXT NOT NULL,
            definition TEXT NOT NULL,
            synonyms TEXT NOT NULL,
            category TEXT NOT NULL
        )
    ''')
    cur.execute('CREATE INDEX idx_word_difficulty ON words(difficulty)')
    cur.execute('CREATE INDEX idx_word_category ON words(category)')
    cur.execute('CREATE INDEX idx_word_length ON words(length)')

    # Load candidate words from NLTK words dataset + extra rich vocabulary list
    candidate_words = set(w.lower() for w in nltk_words.words() if len(w) >= 3 and len(w) <= 14 and w.isalpha())
    
    extra_words = [
        "algorithm", "alchemy", "asteroid", "aquarium", "avalanche", "bacteria", "biodiversity", "blueprint",
        "boulder", "butterfly", "cathedral", "chameleon", "chronicle", "cinnamon", "constellation", "cyberpunk",
        "dinosaur", "eclipse", "ecosystem", "emerald", "ephemeral", "flamingo", "galaxy", "glacier", "gravity",
        "hologram", "horizon", "hyperloop", "illusion", "infinity", "jungle", "kaleidoscope", "labyrinth", "lagoon",
        "lantern", "lightning", "magnet", "meteor", "metropolis", "microscope", "molecule", "monolith", "nebula",
        "oasis", "obsidian", "ocean", "odyssey", "origami", "paradox", "penguin", "phantom", "phenomenon", "pyramid",
        "quantum", "quicksand", "radiation", "rainbow", "rebellion", "resonance", "robotics", "sanctuary", "sapphire",
        "satellite", "serendipity", "silhouette", "solar", "solitude", "spectrum", "starlight", "supernova", "symbiosis",
        "telescope", "thunder", "tornado", "tsunami", "utopia", "velocity", "volcano", "vortex", "whisper", "wilderness"
    ]
    candidate_words.update(extra_words)

    processed_count = 0
    sql_statements = []

    for word in sorted(candidate_words):
        if not re.match(r'^[a-z]+$', word):
            continue
        
        wn_info = get_wordnet_info(word)
        if not wn_info:
            continue

        length = len(word)
        vowel_cnt = sum(1 for c in word if c in VOWELS)
        cons_cnt = length - vowel_cnt
        has_repeated = len(set(word)) < length

        if HAS_WORDFREQ:
            freq = zipf_frequency(word, 'en')
        else:
            freq = 4.0

        if HAS_WORDFREQ and freq < 1.5 and word not in extra_words:
            continue

        difficulty = calculate_difficulty(word, freq)

        pos = wn_info['pos']
        definition = wn_info['definition'].replace("'", "''")
        synonyms_str = json.dumps(wn_info['synonyms']).replace("'", "''")
        category = wn_info['category']

        cur.execute('''
            INSERT OR IGNORE INTO words 
            (word, length, vowel_count, consonant_count, has_repeated_letters, frequency, difficulty, part_of_speech, definition, synonyms, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (word, length, vowel_cnt, cons_cnt, has_repeated, freq, difficulty, pos, wn_info['definition'], json.dumps(wn_info['synonyms']), category))

        sql_statements.append(
            f"INSERT INTO words (word, length, vowel_count, consonant_count, has_repeated_letters, frequency, difficulty, part_of_speech, definition, synonyms, category) "
            f"VALUES ('{word}', {length}, {vowel_cnt}, {cons_cnt}, {1 if has_repeated else 0}, {freq:.2f}, {difficulty}, '{pos}', '{definition}', '{synonyms_str}', '{category}') ON CONFLICT (word) DO NOTHING;"
        )

        processed_count += 1

    conn.commit()
    conn.close()

    with open(seed_sql_path, 'w', encoding='utf-8') as f:
        f.write("-- Hangman Reimagined Seed Data\n")
        f.write("\n".join(sql_statements))

    print(f"Successfully processed {processed_count} words into {output_db_path} and {seed_sql_path}")

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_p = os.path.join(base_dir, 'backend', 'data', 'words.db')
    seed_p = os.path.join(base_dir, 'supabase', 'seed_words.sql')
    process_word_corpus(db_p, seed_p)
