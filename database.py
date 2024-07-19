import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    input_text TEXT,
                    cleaned_text TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    conn.commit()
    conn.close()

def insert_record(input_text, cleaned_text):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    timestamp = datetime.now()
    c.execute('INSERT INTO records (input_text, cleaned_text, timestamp) VALUES (?, ?, ?)', 
              (input_text, cleaned_text, timestamp))
    conn.commit()
    conn.close()
