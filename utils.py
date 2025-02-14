import orjson
from config import RULES_FILE

def get_rules():
    """Get the rules from the rules file."""
    with open(RULES_FILE, "rb") as f:
        return orjson.loads(f.read())