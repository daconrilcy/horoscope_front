import sqlite3
import os
from datetime import datetime

db_path = "horoscope.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create email_logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS email_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        email_type VARCHAR(50) NOT NULL,
        recipient_email VARCHAR(255) NOT NULL,
        sent_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
        status VARCHAR(20) NOT NULL,
        provider_message_id VARCHAR(255),
        error_message TEXT,
        FOREIGN KEY(user_id) REFERENCES users (id)
    )
    """)
    
    # Add index
    try:
        cursor.execute("CREATE INDEX idx_email_logs_user_type ON email_logs (user_id, email_type)")
    except:
        pass

    # Add email_unsubscribed to users
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN email_unsubscribed BOOLEAN DEFAULT 0 NOT NULL")
    except Exception as e:
        print(f"Users update skip: {e}")

    # Update alembic_version
    cursor.execute("DELETE FROM alembic_version")
    cursor.execute("INSERT INTO alembic_version (version_num) VALUES ('2964d54e4131')")
    
    conn.commit()
    conn.close()
    print("Manual migration apply done.")
else:
    print(f"{db_path} not found.")
