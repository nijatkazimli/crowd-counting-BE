import sqlite3
from flask import g

DATABASE = 'instance/example.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn
