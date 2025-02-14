import os

# Database configuration
DB_PATH = "sqlite:///emails.db"

# Gmail API OAuth credentials and token storage
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"

# Rules JSON file
RULES_FILE = "rules.json"

# Ensure token file exists
if not os.path.exists(TOKEN_FILE):
    open(TOKEN_FILE, "w").close()
