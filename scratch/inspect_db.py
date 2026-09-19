import sqlite3

conn = sqlite3.connect('backend/data/words.db')
cur = conn.cursor()

cur.execute("PRAGMA table_info(words)")
print("Columns:", cur.fetchall())

cur.execute("SELECT * FROM words WHERE word='burke' OR word='burk'")
print("Burke row:", cur.fetchall())

cur.execute("SELECT * FROM words WHERE category='Technology' LIMIT 5")
print("Technology sample:", cur.fetchall())
