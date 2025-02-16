import os

# Database configuration
DB_PATH = "sqlite:///database/emails.db"

# Test database setup
TEST_DB_PATH = "sqlite:///database/test_emails.db"

# Gmail API OAuth credentials and token storage
CREDENTIALS_FILE = "secrets/credentials.json"
TOKEN_FILE = "secrets/token.json"

# Rules JSON file
RULES_FILE = "rules.json"

# Gmail API scopes
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

# Create secrets directory if it doesn't exist
secrets_dir = os.path.dirname(TOKEN_FILE)
if not os.path.exists(secrets_dir):
    os.makedirs(secrets_dir)

# Create token.json file if it doesn't exist
if not os.path.exists(TOKEN_FILE):
    with open(TOKEN_FILE, "w") as f:
        f.write("{}")