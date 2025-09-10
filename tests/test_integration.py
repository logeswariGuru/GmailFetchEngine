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

# --- Mock Classes ---
class MockListRequest:
    def execute(self):
        return {"messages": [{"id": "10"}]}

class MockGetRequest:
    def execute(self):
        return {
            "id": "10",
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
    def list(self, userId, labelIds, maxResults, pageToken=None):
        return MockListRequest()
    def get(self, userId, id, format):
        return MockGetRequest()

class MockUsers:
    def messages(self):
        return MockMessages()

class MockBatch:
    """Simulate Gmail batch request for testing."""
    def __init__(self):
        self.requests = []

    def add(self, request, callback=None):
        try:
            response = request.execute()
            if callback:
                callback(request_id=response.get("id"), response=response, exception=None)
        except Exception as e:
            if callback:
                callback(request_id=None, response=None, exception=e)

    def execute(self):
        pass  # No-op, already processed in add

class MockService:
    def users(self):
        return MockUsers()
    def new_batch_http_request(self):
        return MockBatch()

# --- Integration Test ---
class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        # Create temp DB path
        self.db_path = os.path.join(os.path.dirname(__file__), "it_emails.db")
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.environ["GMAIL_DB_FILE"] = self.db_path

        # reload repository to pick up env var
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
        # 1) Fetch via mocked service
        service = MockService()
        emails, _ = fetch_inbox_messages(service, max_results=1)
        self.assertEqual(len(emails), 1, "Expected one email fetched from Gmail")

        # 2) Save to DB
        self.repo.save_emails(emails)

        # 3) Verify in DB
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM emails;")
        count = cur.fetchone()[0]
        conn.close()

        self.assertEqual(count, 1, "Expected one email stored in DB")

        # 4) Verify email content
        stored_email = self.repo.fetch_all_emails()[0]
        self.assertEqual(stored_email["from"], "it@example.com")
        self.assertEqual(stored_email["subject"], "IT Subject")
        self.assertEqual(stored_email["snippet"], "Integration test message")

if __name__ == "__main__":
    unittest.main()
