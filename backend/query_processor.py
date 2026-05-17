import sqlite3
import os
from datetime import datetime

class QueryProcessor:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, 'database', 'history.db')
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                symptoms TEXT,
                diagnosis TEXT,
                confidence REAL
            )
        ''')
        self.conn.commit()

    def log_query(self, symptoms, diagnosis, confidence):
        cursor = self.conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        symptoms_str = ", ".join(symptoms)
        cursor.execute('''
            INSERT INTO queries (timestamp, symptoms, diagnosis, confidence)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, symptoms_str, diagnosis, confidence))
        self.conn.commit()

    def get_history(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM queries ORDER BY id DESC")
        return cursor.fetchall()
