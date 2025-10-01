import sqlite3
import os

DB_PATH = "database/dbdb"  
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS publications')

cursor.execute('''
CREATE TABLE IF NOT EXISTS publications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    summary TEXT,
    tags TEXT,
    year INTEGER,
    organization TEXT,
    country TEXT,
    language TEXT,
    pdf_path TEXT,
    original_link TEXT
)
''')

# cursor.execute('''
# ALTER TABLE publications ADD CONSTRAINT unique_title UNIQUE (title)
# ''')

conn.commit()
conn.close()
print("DB schema created.")