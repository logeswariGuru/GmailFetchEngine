"""Builds Gmail API service."""

import logging
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


def build_service(creds: Credentials):
    """Build and return Gmail API service client."""
    try:
        service = build("gmail", "v1", credentials=creds)
        logging.info("Gmail service built successfully.")
        return service
    except Exception as e:
        logging.error(f"Failed to build Gmail service: {e}")
        raise
