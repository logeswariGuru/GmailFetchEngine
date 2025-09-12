"""Entry point for Gmail client app with CLI options."""

import logging
import argparse
from gmail_client.auth import authenticate
from gmail_client.gmail_service import build_service
from gmail_client.email_fetch import fetch_all_emails_from_gmail, fetch_inbox_messages
from gmail_client.email_repository import init_db, save_emails
from gmail_client.rule_processor.rule_engine import process_rules

def fetch_emails(service, fetch_all: bool = True, batch_size: int = 50):
    """
    Fetch emails from Gmail based on user choice.
    
    Args:
        service: Gmail API service instance.
        fetch_all (bool): If True, fetch all emails using batching.
                          If False, fetch only the first `batch_size`.
        batch_size (int): Number of emails per page/batch.
    Returns:
        List of email dictionaries.
    """
    if fetch_all:
        logging.info("📩 Fetching ALL emails using batch processing...")
        return fetch_all_emails_from_gmail(service, batch_size=batch_size)
    else:
        logging.info(f"📩 Fetching ONLY first {batch_size} emails...")
        emails, _ = fetch_inbox_messages(service, max_results=batch_size)
        return emails


def main(fetch_all: bool = True, batch_size: int = 50):
    """Authenticate, fetch emails, save to DB, and process rules."""
    try:
        # 1. Initialize DB
        init_db()

        # 2. Authenticate and build Gmail service
        creds = authenticate()
        service = build_service(creds)

        # 3. Fetch emails dynamically
        emails = fetch_emails(service, fetch_all=fetch_all, batch_size=batch_size)

        # 4. Save all emails to DB
        if emails:
            logging.info(f"Saving {len(emails)} emails to DB...")
            save_emails(emails)
        else:
            logging.info("No emails retrieved from Gmail.")

        # # 5. Fetch from DB to verify persistence (optional)
        # stored_emails = fetch_all_emails()

        # 6. Process rules on stored emails
        process_rules(service)

    except Exception as e:
        logging.error(f"Application error: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="Gmail Fetch Client")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true", help="Fetch ALL emails with batch processing")
    group.add_argument("--first", type=int, help="Fetch only the first N emails")
    parser.add_argument("--batch-size", type=int, default=50, help="Batch size for fetching emails")

    args = parser.parse_args()

    if args.all:
        main(fetch_all=True, batch_size=args.batch_size)
    elif args.first:
        main(fetch_all=False, batch_size=args.first)
