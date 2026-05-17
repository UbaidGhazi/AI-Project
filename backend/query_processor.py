import sqlite3
import os
from datetime import datetime

class QueryProcessor:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_dir = os.path.join(base_dir, 'database')
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
        db_path = os.path.join(db_dir, 'history.db')
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_table()
        self.seed_if_empty()

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

    def seed_if_empty(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM queries")
        count = cursor.fetchone()[0]
        if count == 0:
            mock_data = [
                ("2026-05-15 08:30:12", "fever, cough, fatigue, sore_throat", "flu", 80.0),
                ("2026-05-15 10:14:45", "headache, nausea, sensitivity_to_light", "migraine", 75.0),
                ("2026-05-15 11:42:01", "cough, chest_pain, shortness_of_breath, wheezing", "asthma", 100.0),
                ("2026-05-16 09:05:22", "fever, cough, loss_of_taste, shortness_of_breath", "covid", 66.7),
                ("2026-05-16 14:22:10", "headache, fatigue, chest_pain", "hypertension", 75.0),
                ("2026-05-16 16:50:33", "fatigue, increased_thirst, frequent_urination", "diabetes", 75.0),
                ("2026-05-17 10:10:05", "sneezing, runny_nose, itchy_eyes", "allergies", 75.0),
                ("2026-05-17 11:30:44", "fever, cough, chest_pain, difficulty_breathing", "pneumonia", 80.0),
                ("2026-05-17 15:18:29", "headache, nausea, visual_aura", "migraine", 75.0),
                ("2026-05-17 17:45:00", "fever, cough, sore_throat", "flu", 60.0),
            ]
            cursor.executemany('''
                INSERT INTO queries (timestamp, symptoms, diagnosis, confidence)
                VALUES (?, ?, ?, ?)
            ''', mock_data)
            self.conn.commit()
