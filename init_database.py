"""
Database initialization script for the AI Productivity Framework.

This script creates the SQLite database with the Observations table.
"""

import sqlite3
import os


def init_database(db_name="productivity_framework.db"):
    """
    Initialize the SQLite database with the Observations table.
    
    Args:
        db_name (str): Name of the database file. Defaults to 'productivity_framework.db'
    """
    # Check if database already exists
    if os.path.exists(db_name):
        print(f"Database '{db_name}' already exists. Skipping initialization.")
        return
    
    # Create connection to database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Create Observations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            value REAL NOT NULL,
            commit_hash TEXT,
            deployment_id INTEGER,
            deployment_failure_id INTEGER,
            ai_rework_commit INTEGER,
            FOREIGN KEY (deployment_id) REFERENCES observations(id),
            FOREIGN KEY (deployment_failure_id) REFERENCES observations(id)
        )
    """)
    
    # Create index on type for faster queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_type 
        ON observations(type)
    """)
    
    # Create index on timestamp for faster queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp 
        ON observations(timestamp)
    """)
    
    conn.commit()
    conn.close()
    
    print(f"Database '{db_name}' initialized successfully!")
    print("Table 'observations' created with columns: id, type, timestamp, value, commit_hash, deployment_id, deployment_failure_id, ai_rework_commit")


if __name__ == "__main__":
    init_database()
