import os
import sqlite3
import unittest
from importlib import reload

# Ensure project root is on sys.path
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from gmail_client.email_fetch import fetch_inbox_messages

class MockListRequest:
    def execute(self):
        return {"messages": [{"id": "10"}]}

class MockGetRequest:
    def execute(self):
        return {
            "snippet": "Integration test message",
            "labelIds": ["INBOX", "UNREAD"],
            "payload": {
                "headers": [
                    {"name": "From", "value": "it@example.com"},
                    {"name": "Subject", "value": "IT Subject"},
                    {"name": "Date", "value": "Mon, 08 Sep 2025 12:00:00 +0000"},
                ]
            }
        }

class MockMessages:
    def list(self, userId, labelIds, maxResults):
        return MockListRequest()
    def get(self, userId, id, format):
        return MockGetRequest()

class MockUsers:
    def messages(self):
        return MockMessages()

class MockService:
    def users(self):
        return MockUsers()

class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        # Create temp DB path
        self.db_path = os.path.join(os.path.dirname(__file__), "it_emails.db")
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.environ["GMAIL_DB_FILE"] = self.db_path

        # reload config & repository to pick env var
        from config import db_config
        reload(db_config)

        from gmail_client import email_repository as repo
        reload(repo)

        self.repo = repo
        self.repo.init_db()

    def tearDown(self):
        try:
            os.remove(self.db_path)
        except FileNotFoundError:
            pass
        os.environ.pop("GMAIL_DB_FILE", None)

    def test_pipeline_fetch_and_store(self):
        # 1) fetch via mocked service
        service = MockService()
        emails = fetch_inbox_messages(service, max_results=1)
        self.assertEqual(len(emails), 1)

        # 2) save to DB
        self.repo.save_emails(emails)

        # 3) verify in DB
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM emails;")
        count = cur.fetchone()[0]
        conn.close()

        self.assertEqual(count, 1, "Expected one email stored in DB")

if __name__ == "__main__":
    unittest.main()
