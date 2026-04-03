import sqlite3
import os

db_path = "horoscope.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE users DROP COLUMN email_unsubscribed")
        conn.commit()
        print("Column dropped.")
    except Exception as e:
        print(f"Error: {e}")
    conn.close()
