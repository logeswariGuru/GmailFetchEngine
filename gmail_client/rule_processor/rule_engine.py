import json
import os
import logging
from gmail_client.rule_processor.actions import apply_actions
from gmail_client.errors import (
    RULES_FILE_NOT_FOUND,
    RULES_PARSE_FAILED,
    RULE_PARSE_DATE_FAILED,
    RULE_INVALID_CONDITION,
    RULE_UNSUPPORTED_DATE_OPERATOR,
    RULE_UNSUPPORTED_OPERATOR,
    RULE_EVAL_ERROR,
    RULE_UNSUPPORTED_PREDICATE,
    RULE_PROCESS_FAILED,
)
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from gmail_client.email_repository import fetch_all_emails

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

RULES_FILE = os.path.join(os.path.dirname(__file__), "../..", "config", "rules.json")


def load_rules():
    """Load rules from JSON file safely."""
    try:
        with open(RULES_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(RULES_FILE_NOT_FOUND, RULES_FILE)
        return []
    except json.JSONDecodeError as e:
        logger.error(RULES_PARSE_FAILED, e)
        return []


def parse_date_safe(received_at):
    """Try multiple strategies to parse dates from Gmail headers or stored ISO format."""
    if not received_at:
        return None

    try:
        # First try ISO 8601 (our stored format)
        return datetime.fromisoformat(received_at)
    except Exception:
        pass

    try:
        # Then try Gmail RFC2822 header format
        return parsedate_to_datetime(received_at)
    except Exception:
        logger.error(RULE_PARSE_DATE_FAILED, received_at)
        return None


def check_condition(email, condition):
    """Evaluate a single condition on an email with error handling."""
    try:
        field = condition.get("field", "").lower()
        operator = condition.get("operator")
        value = condition.get("value")

        if not field or not operator:
            logger.warning(RULE_INVALID_CONDITION, condition)
            return False

        # Extract field value
        email_val = ""
        if field == "from":
            email_val = email.get("from", "")
        elif field == "to":
            email_val = email.get("to", "")
        elif field == "subject":
            email_val = email.get("subject", "")
        elif field == "datereceived":
            received_at = email.get("received_at")
            email_date = parse_date_safe(received_at)
            if not email_date:
                return False

            now = datetime.now(timezone.utc)

            if operator == "less_than_days":
                return (now - email_date).days < int(value)
            elif operator == "greater_than_days":
                return (now - email_date).days > int(value)
            elif operator == "less_than_months":
                return (now - email_date).days < int(value) * 30
            elif operator == "greater_than_months":
                return (now - email_date).days > int(value) * 30
            else:
                logger.warning(RULE_UNSUPPORTED_DATE_OPERATOR, operator)
                return False

        # Handle string operators
        if isinstance(email_val, str):
            if operator == "contains":
                return value.lower() in email_val.lower()
            elif operator == "not_contains":
                return value.lower() not in email_val.lower()
            elif operator == "equals":
                return email_val.lower() == value.lower()
            elif operator == "not_equals":
                return email_val.lower() != value.lower()

        logger.warning(RULE_UNSUPPORTED_OPERATOR, operator)
        return False

    except Exception as e:
        logger.error(RULE_EVAL_ERROR, condition, e)
        return False


def process_rules(service):
    """Process emails against rules and apply actions."""
    # 5. Fetch from DB to verify persistence (optional)
    stored_emails = fetch_all_emails()
    if not stored_emails:
        logger.info("ℹ️ No stored emails to process rules on.")
        return
    
    rules = load_rules()
    if not rules:
        logger.info("ℹ️ No rules found to apply.")
        return

    for email in stored_emails:
        for rule in rules:
            conditions = rule.get("conditions", [])
            predicate = rule.get("predicate", "all").lower()
            try:
                if predicate == "all":
                    match = all(check_condition(email, c) for c in conditions)
                elif predicate == "any":
                    match = any(check_condition(email, c) for c in conditions)
                else:
                    logger.warning(RULE_UNSUPPORTED_PREDICATE, predicate)
                    match = False
                if match:
                    logger.info("✅ Rule matched: %s", rule.get("description", "Unnamed"))
                    logger.info(f"apply_action yet to trigger")
                    apply_actions(service, email, rule.get("actions", []))
            except Exception as e:
                logger.error(RULE_PROCESS_FAILED, rule, e)
