import sqlite3
import os

os.makedirs('instance', exist_ok=True)

def init_db():
    conn = sqlite3.connect('instance/crowd-counting.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS crowdCounting (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            annotated_url TEXT,
            averageCountPerFrame REAL,
            model_id INTEGER,
            FOREIGN KEY (model_id) REFERENCES models (id)
        )
    ''')
    
    # TODO: Daniel to add actual models
    models = [
        ('Model A',),
        ('Model B',),
        ('Model C',)
    ]
    
    for model in models:
        c.execute('SELECT COUNT(*) FROM models WHERE name=?', model)
        if c.fetchone()[0] == 0:
            c.execute('INSERT INTO models (name) VALUES (?)', model)
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
