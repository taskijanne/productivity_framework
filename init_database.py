"""
Database initialization script for the AI Productivity Framework.

This script creates the SQLite database with the Projects and Observations tables.
"""

import sqlite3
import os


def init_database(db_name="productivity_framework.db"):
    """
    Initialize the SQLite database with the Projects and Observations tables.
    
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
    
    # Create Projects table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    
    # Create Observations table with project_id foreign key
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            value REAL NOT NULL,
            commit_hash TEXT,
            deployment_id INTEGER,
            deployment_failure_id INTEGER,
            ai_rework_commit INTEGER,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (deployment_id) REFERENCES observations(id),
            FOREIGN KEY (deployment_failure_id) REFERENCES observations(id)
        )
    """)
    
    # Create index on project_id for faster queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_project_id 
        ON observations(project_id)
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
    
    # Create composite index on project_id and type for faster queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_project_type 
        ON observations(project_id, type)
    """)
    
    conn.commit()
    conn.close()
    
    print(f"Database '{db_name}' initialized successfully!")
    print("Table 'projects' created with columns: id, name")
    print("Table 'observations' created with columns: id, project_id, type, timestamp, value, commit_hash, deployment_id, deployment_failure_id, ai_rework_commit")


if __name__ == "__main__":
    init_database()
