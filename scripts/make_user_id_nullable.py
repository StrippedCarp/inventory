import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'inventory.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # SQLite doesn't support ALTER COLUMN directly, need to recreate table
    cursor.execute('''
        CREATE TABLE activity_logs_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            user_id INTEGER,
            username VARCHAR(100) NOT NULL,
            action VARCHAR(50) NOT NULL,
            resource_type VARCHAR(50) NOT NULL,
            resource_name VARCHAR(200) NOT NULL,
            description VARCHAR(500) NOT NULL,
            created_at DATETIME NOT NULL,
            FOREIGN KEY (organization_id) REFERENCES organizations(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        INSERT INTO activity_logs_new 
        SELECT * FROM activity_logs
    ''')
    
    cursor.execute('DROP TABLE activity_logs')
    cursor.execute('ALTER TABLE activity_logs_new RENAME TO activity_logs')
    
    conn.commit()
    print("Successfully made user_id nullable in activity_logs table")
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")
finally:
    conn.close()
