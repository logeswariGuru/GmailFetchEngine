"""Functions for fetching emails from Gmail."""

import logging
from typing import List, Dict
from googleapiclient.errors import HttpError
from datetime import datetime


def fetch_inbox_messages(service, max_results: int = 10) -> List[Dict]:
    """Fetch recent emails from Gmail inbox."""
    try:
        results = service.users().messages().list(
            userId="me", labelIds=["INBOX"], maxResults=max_results
        ).execute()

        messages = results.get("messages", [])
        if not messages:
            logging.info("No messages found in Inbox.")
            return []

        emails = []
        for msg in messages:
            message = service.users().messages().get(
                userId="me", id=msg["id"], format="metadata"
            ).execute()

            headers = message.get("payload", {}).get("headers", [])
            logging.info("headers")
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(No Subject)")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "(Unknown Sender)")
            date_str = next((h["value"] for h in headers if h["name"] == "Date"), None)
            logging.info("data from headers.")
            # Parse received_at from "Date" header
            received_at = None
            if date_str:
                try:
                    logging.info("datetime for parse", date_str)
                    received_at = datetime.strptime(date_str[:25], "%a, %d %b %Y %H:%M:%S")
                    logging.info("received_at:", received_at)
                except Exception:
                    logging.error("Exception from date parse")
                    received_at = date_str  # fallback as string

            # Gmail provides labels
            labels = message.get("labelIds", [])

            # unread status = check for "UNREAD" label
            is_read = 0 if "UNREAD" in labels else 1

            emails.append({
                "id": msg["id"],
                "subject": subject,
                "from": sender,
                "snippet": message.get("snippet"),
                "received_at": str(received_at) if received_at else None,
                "is_read": is_read,
                "labels": labels,
            })
        
        return emails

    except HttpError as e:
        logging.error(f"Gmail API error: {e}")
        return []
    except Exception as e:
        logging.error(f"Unexpected error fetching emails: {e}")
        return []
