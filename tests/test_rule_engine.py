import unittest
import datetime
# Ensure project root is on sys.path
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from gmail_client.rule_processor.rule_engine import check_condition

class TestRuleEngine(unittest.TestCase):
    def setUp(self):
        # Example email with required fields
        self.email = {
            "id": "123",
            "from": "sender@example.com",
            "to": "me@example.com",
            "subject": "Test Subject",
            "body": "This is the body text",
            "received_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "is_read": 0,
            "labels": ["INBOX", "UNREAD"],
        }

    def test_contains_subject(self):
        cond = {"field": "Subject", "operator": "contains", "value": "Test"}
        result = check_condition(self.email, cond)
        self.assertTrue(result)

    def test_not_contains_body(self):
        cond = {"field": "Message", "operator": "not_contains", "value": "xyz"}
        result = check_condition(self.email, cond)
        self.assertTrue(result)

    def test_equals_from(self):
        cond = {"field": "From", "operator": "equals", "value": "sender@example.com"}
        result = check_condition(self.email, cond)
        self.assertTrue(result)

    def test_date_less_than_days(self):
        cond = {"field": "DateReceived", "operator": "less_than_days", "value": 2}
        result = check_condition(self.email, cond)
        self.assertTrue(result)

    def test_date_greater_than_months(self):
        old_email = dict(self.email)
        old_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=200)).isoformat()
        old_email["received_at"] = old_date

        cond = {"field": "DateReceived", "operator": "greater_than_months", "value": 6}
        result = check_condition(old_email, cond)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
