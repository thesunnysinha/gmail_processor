import orjson
from config import RULES_FILE

def get_rules():
    with open(RULES_FILE, "rb") as f:
        return orjson.loads(f.read())