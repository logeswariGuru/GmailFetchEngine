"""Centralized log message templates and error strings for GmailFetchEngine.

Keeping message templates here makes it easier to update wording or translations later.
"""

# Generic markers
ERROR_MARK = "❌"
WARN_MARK = "⚠️"
INFO_MARK = "ℹ️"

# Rule engine
RULES_FILE_NOT_FOUND = f"{ERROR_MARK} Rules file not found: %s"
RULES_PARSE_FAILED = f"{ERROR_MARK} Failed to parse rules.json: %s"
RULE_PARSE_DATE_FAILED = f"{ERROR_MARK} Could not parse date: %s"
RULE_INVALID_CONDITION = f"{WARN_MARK} Invalid condition: %s"
RULE_UNSUPPORTED_DATE_OPERATOR = f"{WARN_MARK} Unsupported date operator: %s"
RULE_UNSUPPORTED_OPERATOR = f"{WARN_MARK} Unsupported operator: %s"
RULE_EVAL_ERROR = f"{ERROR_MARK} Error evaluating condition %s: %s"
RULE_UNSUPPORTED_PREDICATE = f"{WARN_MARK} Unsupported rule predicate: %s"
RULE_PROCESS_FAILED = f"{ERROR_MARK} Failed to process rule %s: %s"

# Actions
ACTIONS_NO_DESTINATION = f"{WARN_MARK} No destination provided for move action."
ACTIONS_UNSUPPORTED = f"{WARN_MARK} Unsupported action type: %s"
ACTIONS_APPLY_FAILED = f"{ERROR_MARK} Failed to apply action %s on email %s: %s"

# Email fetch
EMAIL_PARSE_HEADER_FAILED = f"{WARN_MARK} Failed to parse header date: %s, error: %s"
EMAIL_PARSE_INTERNALDATE_FAILED = f"{ERROR_MARK} Failed to parse internalDate: %s"
EMAIL_FETCH_ERROR = f"{ERROR_MARK} Error fetching message %s: %s"
EMAIL_PROCESS_FAILED = f"{ERROR_MARK} Failed to process message: %s"
EMAIL_RATE_LIMITED = f"{WARN_MARK} Rate limited (429). Retrying in %s..."
EMAIL_GMAIL_API_ERROR = f"Gmail API error: %s"
EMAIL_UNEXPECTED_FETCH_ERROR = f"Unexpected error fetching emails: %s"
EMAIL_MAX_RETRIES_EXCEEDED = "Max retries exceeded due to Gmail rate limits"

# DB
DB_INIT_FAILED = "Failed to initialize database: %s"
DB_SAVE_FAILED = "Failed to save emails: %s"
DB_FETCH_FAILED = "Failed to fetch emails from DB: %s"

# Gmail service
GMAIL_SERVICE_FAILED = "Failed to build Gmail service: %s"
