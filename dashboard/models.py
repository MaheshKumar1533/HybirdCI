import sqlite3

def init_db():
    conn = sqlite3.connect("ci.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tests_run INTEGER,
            time_taken REAL,
            cache_hit INTEGER
        )
    """)
    conn.commit()
    conn.close()
