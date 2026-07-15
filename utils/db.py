import sqlite3
import json
import os
from datetime import datetime

DB_PATH = "siteverify.db"

def get_connection():
    """
    Returns a connection to the SQLite database.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes the database schema if it doesn't already exist.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT,
            timestamp TEXT NOT NULL,
            overall_score REAL NOT NULL,
            grade TEXT,
            status TEXT,
            screenshot_path TEXT,
            report_json TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_scan(url, title, overall_score, grade, status, screenshot_path, report_dict):
    """
    Saves a scan record and the full report JSON.
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    report_json = json.dumps(report_dict)
    
    cursor.execute("""
        INSERT INTO scans (url, title, timestamp, overall_score, grade, status, screenshot_path, report_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (url, title, timestamp, overall_score, grade, status, screenshot_path, report_json))
    
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id

def get_scan_history():
    """
    Retrieves the entire scan history sorted by most recent first.
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, url, title, timestamp, overall_score, grade, status, screenshot_path
        FROM scans
        ORDER BY timestamp DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_scan_by_id(scan_id):
    """
    Retrieves a single detailed scan report by ID.
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        result = dict(row)
        result["report"] = json.loads(result["report_json"])
        return result
    return None

def get_url_history(url):
    """
    Retrieves score progress for a specific URL.
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, timestamp, overall_score 
        FROM scans 
        WHERE url = ? 
        ORDER BY timestamp ASC
    """, (url,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_scan(scan_id):
    """
    Deletes a scan record by ID.
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
    conn.commit()
    conn.close()

def get_aggregate_stats():
    """
    Calculates summary stats of all scans in the system.
    """
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM scans")
    total_scans = cursor.fetchone()[0]
    
    if total_scans == 0:
        conn.close()
        return {
            "total_scans": 0,
            "avg_score": 0.0,
            "highest_score": 0.0,
            "unique_domains": 0
        }
        
    cursor.execute("SELECT AVG(overall_score) FROM scans")
    avg_score = round(cursor.fetchone()[0], 1)
    
    cursor.execute("SELECT MAX(overall_score) FROM scans")
    highest_score = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT url) FROM scans")
    unique_domains = cursor.fetchone()[0]
    
    conn.close()
    return {
        "total_scans": total_scans,
        "avg_score": avg_score,
        "highest_score": highest_score,
        "unique_domains": unique_domains
    }
