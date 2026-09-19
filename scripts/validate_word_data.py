import sqlite3
import os
import json
import sys

def validate():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(base_dir, 'backend', 'data', 'words.db')

    if not os.path.exists(db_path):
        print(f"Error: Database {db_path} does not exist.")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM words")
    total_words = cur.fetchone()[0]
    print(f"Total processed words: {total_words}")

    if total_words < 500:
        print("Warning: Word count is unusually low!")

    # Check difficulty breakdown
    cur.execute("SELECT difficulty, COUNT(*) FROM words GROUP BY difficulty")
    diff_counts = dict(cur.fetchall())
    print(f"Difficulty breakdown: {diff_counts}")

    # Check category breakdown
    cur.execute("SELECT category, COUNT(*) FROM words GROUP BY category")
    cat_counts = dict(cur.fetchall())
    print(f"Category breakdown: {cat_counts}")

    # Sample check for invalid definitions or missing fields
    cur.execute("SELECT word, length, vowel_count, consonant_count, definition, category FROM words WHERE definition IS NULL OR definition = '' LIMIT 10")
    invalid = cur.fetchall()
    if invalid:
        print(f"Found {len(invalid)} words with missing definitions!")
    else:
        print("All words have valid definitions and metadata!")

    conn.close()

if __name__ == '__main__':
    validate()
