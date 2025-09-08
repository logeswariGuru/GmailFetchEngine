"""Entry point for Gmail client app."""

import logging
from gmail_client.auth import authenticate
from gmail_client.gmail_service import build_service
from gmail_client.email_fetch import fetch_inbox_messages
from gmail_client.email_repository import init_db, save_emails, fetch_all_emails


def main():
    """Authenticate and fetch emails."""
    try:
         # 1. Initialize DB (creates "emails" table if not exists)
        init_db()
         # 2. Authenticate and build Gmail service
        creds = authenticate()
        service = build_service(creds)
        # 3. Fetch emails from Gmail API
        emails = fetch_inbox_messages(service, max_results=5)
        logging.info("from main: emails*:", emails)
        # 4. Save them directly into DB
        if emails:
            logging.info("Recent Emails:")
            save_emails(emails)
            # for email in emails:
            #     print(f"From: {email['from']} | Subject: {email['subject']}")
        else:
            logging.info("No emails retrieved.")
        # 5. Fetch from DB to verify persistence
        stored_emails = fetch_all_emails()
        logging.info(f"DB contains {len(stored_emails)} emails.")

        for email in stored_emails[:5]:
            print(f"[{email['received_at']}] From: {email['from']} | Subject: {email['subject']}")


    except Exception as e:
        logging.error(f"Application error: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    main()
