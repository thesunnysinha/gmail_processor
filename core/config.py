import os

# Database configuration
DB_PATH = "sqlite:///emails.db"

# Gmail API OAuth credentials and token storage
CREDENTIALS_FILE = "../secrets/credentials.json"
TOKEN_FILE = "../secrets/token.json"

# Rules JSON file
RULES_FILE = "rules.json"

# Create token.json file if it doesn't exist
if not os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, "w") as f:
        f.write("{}")