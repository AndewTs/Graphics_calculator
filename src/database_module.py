import sqlite3

class DatabaseModule:
    def __init__(self, db_name="graph_calculator.db"):
        self.db_name = db_name
        self.init_database()
        
    def init_database(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                function_text TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def save_query(self, function_text):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO history (function_text) VALUES (?)",
            (function_text,)
        )
        
        conn.commit()
        conn.close()
        
    def get_history(self, limit=50):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM history ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        
        history = cursor.fetchall()
        conn.close()
        
        return history