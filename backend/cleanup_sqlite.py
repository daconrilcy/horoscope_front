import sqlite3
import os

db_path = "horoscope.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '_alembic_tmp_%'")
    tables = cursor.fetchall()
    for t in tables:
        print(f"Dropping {t[0]}")
        cursor.execute(f"DROP TABLE {t[0]}")
    conn.commit()
    conn.close()
    print("Cleanup done.")
else:
    print(f"{db_path} not found.")
