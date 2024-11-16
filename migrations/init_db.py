import sqlite3
import os

os.makedirs('instance', exist_ok=True)

def init_db():
    conn = sqlite3.connect('instance/crowd-counting.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS crowdCounting (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            annotated_url TEXT NOT NULL,
            averageCountPerFrame REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
