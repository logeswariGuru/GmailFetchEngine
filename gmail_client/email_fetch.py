from typing import List, Dict, Optional, Tuple
import logging, time, random
from googleapiclient.errors import HttpError
from datetime import datetime
from email.utils import parsedate_to_datetime


def parse_headers(headers: List[Dict]) -> Dict[str, str]:
    """Convert Gmail headers list to a dictionary with lowercase keys."""
    return {header["name"].lower(): header["value"] for header in headers}

def extract_received_at(date_str: Optional[str], message: Dict) -> Optional[str]:
    """
    Extract and normalize Gmail 'received_at' timestamp as ISO 8601 string.
    """
    received_at: Optional[datetime] = None

    if date_str:
        try:
            received_at = parsedate_to_datetime(date_str)
        except Exception as e:
            logging.warning(f"⚠️ Failed to parse header date: {date_str}, error: {e}")

    if not received_at:
        try:
            internal_ts = int(message.get("internalDate", 0)) / 1000
            received_at = datetime.utcfromtimestamp(internal_ts)
        except Exception as e:
            logging.error(f"❌ Failed to parse internalDate: {e}")
            received_at = None

    return received_at.isoformat() if received_at else None


def process_message_response(
    emails: List[Dict],
    request_id: str,
    response: Dict,
    exception: Optional[Exception]
) -> None:
    """Callback for handling each Gmail message in batch request."""
    if exception:
        logging.error(f"❌ Error fetching message {request_id}: {exception}")
        return

    try:
        headers = response.get("payload", {}).get("headers", [])
        headers_dict = parse_headers(headers)

        subject = headers_dict.get("subject", "(No Subject)")
        sender = headers_dict.get("from", "(Unknown Sender)")
        date_str = headers_dict.get("date")
        received_at = extract_received_at(date_str, response)

        labels = response.get("labelIds", [])
        is_read = 0 if "UNREAD" in labels else 1

        emails.append({
            "id": response["id"],
            "subject": subject,
            "from": sender,
            "snippet": response.get("snippet"),
            "received_at": received_at,
            "is_read": is_read,
            "labels": labels,
        })
    except Exception as e:
        logging.error(f"⚠️ Failed to process message: {e}")


def safe_execute(batch, retries: int = 5):
    """Execute Gmail batch request with exponential backoff on rate limits."""
    for i in range(retries):
        try:
            return batch.execute()
        except HttpError as e:
            if e.resp.status == 429:  # rate limit exceeded
                wait = (2 ** i) + random.random()
                logging.warning(f"Rate limited (429). Retrying in {wait:.1f}s...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Max retries exceeded due to Gmail rate limits")


def fetch_inbox_messages(
    service,
    max_results: int = 50,
    page_token: Optional[str] = None,
    batch_limit: int = 10,  # 👈 throttle batch size to avoid 429s
) -> Tuple[List[Dict], Optional[str]]:
    """
    Fetch one page of emails from Gmail inbox using batch requests.
    Handles Gmail rate limits with retries and smaller batch sizes.
    Returns:
        (emails, nextPageToken)
    """
    try:
        results: Dict = service.users().messages().list(
            userId="me",
            labelIds=["INBOX"],
            maxResults=max_results,
            pageToken=page_token
        ).execute()

        messages: List[Dict] = results.get("messages", [])
        next_page_token: Optional[str] = results.get("nextPageToken")

        if not messages:
            return [], next_page_token

        emails: List[Dict] = []

        # Process in smaller chunks to avoid hitting Gmail concurrency limits
        for i in range(0, len(messages), batch_limit):
            chunk = messages[i:i + batch_limit]
            batch = service.new_batch_http_request()

            for msg in chunk:
                batch.add(
                    service.users().messages().get(userId="me", id=msg["id"], format="metadata"),
                    callback=lambda request_id, response, exception: process_message_response(
                        emails, request_id, response, exception
                    )
                )

            safe_execute(batch)  # 👈 use retry wrapper

        return emails, next_page_token

    except HttpError as e:
        logging.error(f"Gmail API error: {e}")
        return [], None
    except Exception as e:
        logging.error(f"Unexpected error fetching emails: {e}")
        return [], None


def fetch_all_emails_from_gmail(service, batch_size: int = 50, batch_limit: int = 10) -> List[Dict]:
    """
    Fetch all emails from Gmail inbox using batch requests and nextPageToken.
    Returns a list of email dictionaries.
    """
    all_emails: List[Dict] = []

    emails, next_token = fetch_inbox_messages(service, max_results=batch_size, batch_limit=batch_limit)
    if emails:
        logging.info(f"Fetched {len(emails)} emails from Gmail (first batch).")
        all_emails.extend(emails)

    while next_token:
        emails, next_token = fetch_inbox_messages(service, max_results=batch_size, page_token=next_token, batch_limit=batch_limit)
        if emails:
            logging.info(f"Fetched {len(emails)} emails from Gmail (next batch).")
            all_emails.extend(emails)

    logging.info(f"Total emails fetched: {len(all_emails)}")
    return all_emails
