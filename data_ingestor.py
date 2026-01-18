"""
Data ingestion script for the AI Productivity Framework.

This script reads data from a CSV file and ingests it into the SQLite database.
"""

import sqlite3
import csv
import os
from datetime import datetime

from models import ObservationType


def ingest_data(csv_file="sample_data.csv", db_name="productivity_framework.db"):
    """
    Ingest data from CSV file into the Observations table.
    
    Args:
        csv_file (str): Path to the CSV file containing the data
        db_name (str): Name of the database file
    """
    # Check if database exists
    if not os.path.exists(db_name):
        print(f"Error: Database '{db_name}' not found!")
        print("Please run 'python init_database.py' first to create the database.")
        return
    
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found!")
        return
    
    # Connect to database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Read and insert data from CSV
    records_inserted = 0
    records_skipped = 0
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        # Use semicolon as delimiter for European CSV format
        csv_reader = csv.DictReader(file, delimiter=';')
        
        for row in csv_reader:
            try:
                # Get id if present in CSV
                record_id = int(row['id']) if row.get('id') and row['id'] else None
                
                type_value = row['type']
                
                # Validate observation type
                valid_types = [obs_type.value for obs_type in ObservationType]
                if type_value not in valid_types:
                    raise ValueError(f"Invalid observation type: '{type_value}'. Must be one of: {', '.join(valid_types)}")
                
                timestamp = row['timestamp']
                
                # Convert European decimal format (comma) to standard format (dot)
                value_str = row['value'].replace(',', '.')
                value = float(value_str)
                
                commit_hash = row.get('commit_hash') if row.get('commit_hash') else None
                deployment_id = int(row['deployment_id']) if row.get('deployment_id') and row['deployment_id'] else None
                deployment_failure_id = int(row['deployment_failure_id']) if row.get('deployment_failure_id') and row['deployment_failure_id'] else None
                ai_rework_commit = int(row['ai_rework_commit']) if row.get('ai_rework_commit') and row['ai_rework_commit'] else None
                
                # Insert with specific ID if provided, otherwise let it auto-increment
                if record_id is not None:
                    cursor.execute("""
                        INSERT INTO observations (id, type, timestamp, value, commit_hash, deployment_id, deployment_failure_id, ai_rework_commit)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (record_id, type_value, timestamp, value, commit_hash, deployment_id, deployment_failure_id, ai_rework_commit))
                else:
                    cursor.execute("""
                        INSERT INTO observations (type, timestamp, value, commit_hash, deployment_id, deployment_failure_id, ai_rework_commit)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (type_value, timestamp, value, commit_hash, deployment_id, deployment_failure_id, ai_rework_commit))
                
                records_inserted += 1
                
            except Exception as e:
                print(f"Error inserting row {row}: {e}")
                records_skipped += 1
                continue
    
    conn.commit()
    conn.close()
    
    print(f"Successfully ingested {records_inserted} records from '{csv_file}' into '{db_name}'")
    if records_skipped > 0:
        print(f"Skipped {records_skipped} records due to errors")


if __name__ == "__main__":
    ingest_data()
