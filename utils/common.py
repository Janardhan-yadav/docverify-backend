import re

def normalize_text(text: str) -> str:
    """Normalize text by removing extra spaces and converting to uppercase."""
    return " ".join(text.strip().upper().split())

# Common regex patterns
NAME_PATTERN = r"[A-Z]+ [A-Z]+(?: [A-Z]+)?"
HALL_TICKET_PATTERN = r"^\d{10}$"
CATEGORY_PATTERN = r"^(OC|SC|ST|BC)$"
ROLL_NO_PATTERN = r"^[A-Z0-9]{8,}$"
APPLICATION_NO_PATTERN = r"^[A-Z0-9]{8,}$"
NUMBER_PATTERN = r"\d+(\.\d+)?"
DATE_PATTERN = r"\b\d{2}/\d{2}/\d{4}\b"