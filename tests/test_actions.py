import unittest
# Ensure project root is on sys.path
# This ensure python where to find test file
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from gmail_client.rule_processor.actions import apply_actions

class MockModify:
    def __init__(self):
        self.called = []

    def execute(self):
        self.called.append(True)
        return {"status": "ok"}

class MockMessages:
    def modify(self, userId, id, body):
        self.last_call = {"userId": userId, "id": id, "body": body}
        return self.modify_req

    def __init__(self):
        self.modify_req = MockModify()
        self.last_call = None

class MockUsers:
    def __init__(self):
        self.msg = MockMessages()
    def messages(self):
        return self.msg

class MockService:
    def __init__(self):
        self._users = MockUsers()
    def users(self):
        return self._users

class TestActions(unittest.TestCase):
    def setUp(self):
        self.service = MockService()
        self.email = {"id": "123"}

    def test_mark_as_read(self):
        apply_actions(self.service, self.email, [{"type": "mark_as_read"}])
        body = self.service.users().messages().last_call["body"]
        self.assertIn("removeLabelIds", body)
        self.assertIn("UNREAD", body["removeLabelIds"])

    def test_mark_as_unread(self):
        apply_actions(self.service, self.email, [{"type": "mark_as_unread"}])
        body = self.service.users().messages().last_call["body"]
        self.assertIn("addLabelIds", body)
        self.assertIn("UNREAD", body["addLabelIds"])

    def test_move_label(self):
        apply_actions(self.service, self.email, [{"type": "move", "destination": "IMPORTANT"}])
        body = self.service.users().messages().last_call["body"]
        self.assertIn("addLabelIds", body)
        self.assertIn("IMPORTANT", body["addLabelIds"])
        self.assertIn("removeLabelIds", body)
        self.assertIn("INBOX", body["removeLabelIds"])

    def test_invalid_action(self):
        # Should just warn and not throw
        apply_actions(self.service, self.email, [{"type": "unknown"}])


if __name__ == "__main__":
    unittest.main()
