
# GmailFetchEngine

A small utility to fetch messages from Gmail, persist them to a local SQLite database, and apply rule-based actions (mark read/unread, move to labels, etc.). It's designed to be run from the command line and uses the Gmail REST API.

## Features

- Fetch emails (batch or first N) from Gmail
- Store parsed email metadata into a local SQLite database (`data/emails.db`)
- Apply rules (configured in `config/rules.json`) to messages using the Gmail API (mark read/unread, move to labels)
- Simple, well-tested code with unit tests in `tests/`

## Requirements

- Python 3.10+ (tested with 3.11)
- Google API client dependencies (see `requirements.txt` or install the minimal dependencies below)

Install minimal dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

If you want to run the unit tests, install:

```bash
python -m pip install pytest
```

## Configuration

- `credentials.json`: OAuth2 client credentials obtained from Google Cloud Console (placed in repository root).
- `token.json`: OAuth token created after the first run (automatic).
- `config/gmail_config.py`: Contains SCOPES and filenames for credentials/token.
- `config/rules.json`: Rule definitions used by the rule processor.

Make sure the `credentials.json` file is present in the project root and your OAuth client has the Gmail scopes configured. This project uses the `https://www.googleapis.com/auth/gmail.modify` scope.

## Usage

Run the CLI from the project root. Two mutually exclusive modes are supported:

- Fetch ALL emails (paginated/batched):

```bash
python main.py --all --batch-size 100
```

- Fetch only the first N emails:

```bash
python main.py --first 50
```

The `--batch-size` controls page sizes when fetching all messages.

## Database

The project stores emails in `data/emails.db` (SQLite). The schema is created automatically by `gmail_client.email_repository.init_db()` when you run the app.

## Tests

Unit tests live in the `tests/` directory and are runnable with Python's unittest or pytest.

Run with unittest (built-in):

```bash
python -m unittest discover -v
```

Or with pytest:

```bash
pytest -q
```

## Troubleshooting

- If you see `zsh: command not found: pytest`, install pytest with `python -m pip install pytest`.
- If OAuth sign-in fails, verify `credentials.json` is valid and that the OAuth client has the Gmail scope set. Delete `token.json` and re-run to force a fresh OAuth flow.
- If label changes do not appear in Gmail, check that the app is using the correct label IDs (this project currently uses label names like `INBOX`, `UNREAD`, and custom label names provided in rules). The Gmail API expects label IDs; if you're using label names you may need to map names to label IDs.

## Contributing

Contributions are welcome. Suggested workflow:

1. Create a feature branch
2. Run tests: `python -m unittest discover -v`
3. Open a pull request with a clear description

## License

This project is provided without a license specified. Add a LICENSE file if you plan to open-source it.

---

If you'd like, I can also:

- Add a `requirements.txt` or `pyproject.toml` with pinned dependencies
- Add a short Quickstart section that walks through obtaining `credentials.json` from Google Cloud
- Update `config/rules.json` with examples for common rules

Tell me which of those you'd like next and I'll implement it.
