import re


def estimate_tokens(text: str) -> int:
    """Approximate tokens using words, punctuation, and a small message overhead."""
    if not isinstance(text, str):
        raise TypeError("message content must be a string")
    pieces = re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)
    return max(1, (len(pieces) + 3) // 4 + 3)
