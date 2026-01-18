"""
Database connection utilities for the AI Productivity Framework.
"""

import sqlite3


def get_db_connection(db_name="productivity_framework.db"):
    """
    Create a database connection.
    
    Args:
        db_name (str): Name of the database file
        
    Returns:
        sqlite3.Connection: Database connection with row factory configured
    """
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn
