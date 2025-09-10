"""Database layer for storing Gmail emails using SQLite3."""

import sqlite3
import logging
from typing import Dict, List
from config.db_config import DB_FILE

def init_db():
    """Initialize SQLite3 database and create table if not exists."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id TEXT PRIMARY KEY,
                sender TEXT,
                subject TEXT,
                snippet TEXT,
                 received_at DATETIME,
                is_read INTEGER DEFAULT 0,
                labels TEXT
            )
        """)

        conn.commit()
        conn.close()
        logging.info("Database initialized successfully.")
    except Exception as e:
        logging.error(f"Failed to initialize database: {e}")


def save_emails(emails: List[Dict]):
    """Save list of emails to database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        for email in emails:
            print("*:", email)
            cursor.execute("""
                INSERT OR REPLACE INTO emails (id, sender, subject, snippet, received_at, is_read, labels)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                email.get("id"),
                email.get("from"),
                email.get("subject"),
                email.get("snippet"),
                email.get("received_at"),
                0,
                ",".join(email.get("labels", []))
            ))

        conn.commit()
        conn.close()
        logging.info(f"Saved {len(emails)} emails to database.")
    except Exception as e:
        logging.error(f"Failed to save emails: {e}")


def fetch_all_emails() -> List[Dict]:
    """Retrieve all stored emails from the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT id, sender, subject, snippet, received_at, is_read, labels FROM emails")
        rows = cursor.fetchall()

        conn.close()

        emails = []
        for row in rows:
            emails.append({
                "id": row[0],
                "from": row[1],
                "subject": row[2],
                "snippet": row[3],
                "received_at": row[4],
                "is_read": bool(row[5]),
                "labels": row[6].split(",") if row[6] else []
            })

        return emails
    except Exception as e:
        logging.error(f"Failed to fetch emails from DB: {e}")
        return []
