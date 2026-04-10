import os
import sqlite3

db_path = "horoscope.db"
if not os.path.exists(db_path):
    print(f"File {db_path} not found.")
else:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='llm_assembly_configs';"
    )
    print(f"Table exists: {cur.fetchone()}")
    if True:  # Let's see columns if exists
        cur.execute("PRAGMA table_info(llm_assembly_configs);")
        for col in cur.fetchall():
            print(col)
    conn.close()
