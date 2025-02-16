import orjson
from typing import List, Dict, Any
from core.config import RULES_FILE

def get_rules() -> List[Dict[str, Any]]:
    """Get the rules from the rules file."""
    with open(RULES_FILE, "rb") as f:
        return orjson.loads(f.read())