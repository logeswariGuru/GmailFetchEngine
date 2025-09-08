import os
import sqlite3
import unittest
from importlib import reload

# Ensure project root is on sys.path
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# We'll override the DB_FILE via env var to a temp path for this test run
TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_emails.db")

class TestEmailRepository(unittest.TestCase):
    def setUp(self):
        # Point code to a temp DB for isolation
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
        os.environ["GMAIL_DB_FILE"] = TEST_DB_PATH

        # Reload module so it picks env var
        from config import db_config
        reload(db_config)

        from gmail_client import email_repository as repo
        reload(repo)

        self.repo = repo
        self.db_path = TEST_DB_PATH
        self.repo.init_db()

    def tearDown(self):
        try:
            os.remove(self.db_path)
        except FileNotFoundError:
            pass
        os.environ.pop("GMAIL_DB_FILE", None)

    def test_init_db_creates_table(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='emails';")
        table = cur.fetchone()
        conn.close()
        self.assertIsNotNone(table, "emails table should be created by init_db()")

    def test_save_and_fetch_emails(self):
        emails = [
            {
                "id": "m1",
                "from": "a@example.com",
                "subject": "Hello",
                "snippet": "Snippet 1",
                "received_at": "2025-09-08 10:00:00",
                "is_read": 0,
                "labels": ["INBOX", "UNREAD"]
            },
            {
                "id": "m2",
                "from": "b@example.com",
                "subject": "World",
                "snippet": "Snippet 2",
                "received_at": "2025-09-08 11:00:00",
                "is_read": 1,
                "labels": ["INBOX"]
            },
        ]
        self.repo.save_emails(emails)
        fetched = self.repo.fetch_all_emails()
        self.assertEqual(len(fetched), 2)
        self.assertEqual(fetched[0]["id"], "m1")
        self.assertEqual(fetched[0]["from"], "a@example.com")
        self.assertIn("INBOX", fetched[0]["labels"])

if __name__ == "__main__":
    unittest.main()
