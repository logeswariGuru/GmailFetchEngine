"""Handles Google OAuth authentication and token management."""

import os
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from config.gmail_config import SCOPES, CREDENTIALS_FILE, TOKEN_FILE


def authenticate() -> Credentials:
    """Authenticate user via OAuth and return valid Gmail credentials."""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logging.info("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(f"Missing credentials file: {CREDENTIALS_FILE}")
            logging.info("Launching browser for OAuth login...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
            logging.info(f"Saved new credentials to {TOKEN_FILE}")

    return creds
