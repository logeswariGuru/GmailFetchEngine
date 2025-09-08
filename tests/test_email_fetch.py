import unittest

# Ensure project root is on sys.path
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from gmail_client.email_fetch import fetch_inbox_messages

class MockListRequest:
    def execute(self):
        # Simulate Gmail list response with two messages
        return {"messages": [{"id": "1"}, {"id": "2"}]}

class MockGetRequest1:
    def execute(self):
        return {
            "snippet": "First message snippet",
            "labelIds": ["INBOX", "UNREAD"],
            "payload": {
                "headers": [
                    {"name": "From", "value": "sender1@example.com"},
                    {"name": "Subject", "value": "Subject 1"},
                    {"name": "Date", "value": "Mon, 08 Sep 2025 10:15:00 +0000"},
                ]
            }
        }

class MockGetRequest2:
    def execute(self):
        return {
            "snippet": "Second message snippet",
            "labelIds": ["INBOX"],
            "payload": {
                "headers": [
                    {"name": "From", "value": "sender2@example.com"},
                    {"name": "Subject", "value": "Subject 2"},
                    {"name": "Date", "value": "Mon, 08 Sep 2025 11:20:00 +0000"},
                ]
            }
        }

class MockMessages:
    def list(self, userId, labelIds, maxResults):
        return MockListRequest()
    def get(self, userId, id, format):
        return MockGetRequest1() if id == "1" else MockGetRequest2()

class MockUsers:
    def messages(self):
        return MockMessages()

class MockService:
    def users(self):
        return MockUsers()

class TestEmailFetch(unittest.TestCase):
    def test_fetch_inbox_messages_parses_fields(self):
        service = MockService()
        emails = fetch_inbox_messages(service, max_results=2)

        # We expect two results
        self.assertEqual(len(emails), 2)

        # Validate first message
        e1 = emails[0]
        self.assertEqual(e1["id"], "1")
        self.assertEqual(e1["from"], "sender1@example.com")
        self.assertEqual(e1["subject"], "Subject 1")
        self.assertEqual(e1["snippet"], "First message snippet")
        self.assertEqual(e1["is_read"], 0)  # because UNREAD label present
        self.assertIn("INBOX", e1["labels"])

        # Validate second message
        e2 = emails[1]
        self.assertEqual(e2["id"], "2")
        self.assertEqual(e2["from"], "sender2@example.com")
        self.assertEqual(e2["subject"], "Subject 2")
        self.assertEqual(e2["snippet"], "Second message snippet")
        self.assertEqual(e2["is_read"], 1)  # no UNREAD label
        self.assertIn("INBOX", e2["labels"])

if __name__ == "__main__":
    unittest.main()
