import os
import unittest
from datetime import datetime, timezone

# Ensure project root is on sys.path
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from gmail_client.email_fetch import (
    parse_headers,
    extract_received_at,
    process_message_response,
)


class TestEmailFetch(unittest.TestCase):
    def test_parse_headers_normal(self):
        headers = [
            {"name": "From", "value": "alice@example.com"},
            {"name": "Subject", "value": "Hello"},
            {"name": "Date", "value": "Mon, 01 Jan 2024 10:00:00 +0000"},
        ]
        result = parse_headers(headers)

        self.assertEqual(result["from"], "alice@example.com")
        self.assertEqual(result["subject"], "Hello")
        self.assertEqual(result["date"], "Mon, 01 Jan 2024 10:00:00 +0000")

    def test_parse_headers_empty(self):
        result = parse_headers([])
        self.assertEqual(result, {})

    def test_extract_received_at_from_date(self):
        date_str = "Mon, 01 Jan 2024 10:00:00 +0000"
        result = extract_received_at(date_str, {})
        self.assertTrue(result.startswith("2024-01-01T10:00:00"))

    def test_process_message_response_success(self):
        emails = []
        response = {
            "id": "123",
            "snippet": "Hello World",
            "internalDate": "1700000000000",
            "labelIds": ["INBOX", "UNREAD"],
            "payload": {
                "headers": [
                    {"name": "From", "value": "bob@example.com"},
                    {"name": "Subject", "value": "Hi"},
                    {"name": "Date", "value": "Mon, 01 Jan 2024 10:00:00 +0000"},
                ]
            },
        }
        process_message_response(emails, "123", response, None)

        self.assertEqual(len(emails), 1)
        self.assertEqual(emails[0]["from"], "bob@example.com")
        self.assertEqual(emails[0]["subject"], "Hi")
        self.assertEqual(emails[0]["is_read"], 0)  # unread


if __name__ == "__main__":
    unittest.main()
