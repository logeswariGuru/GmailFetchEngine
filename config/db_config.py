import os

# Default DB file (can be overridden via environment variable)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.getenv("GMAIL_DB_FILE", os.path.join(BASE_DIR, "../data/emails.db"))
