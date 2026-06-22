BLOCKED_PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "system prompt",
    "developer prompt",
    "developer message",
    "reveal prompt",
    "show prompt",
    "api key",
    "secret",
    "password",
    "token",
    "bypass",
    "jailbreak",
    "forget instructions"
]


def validate_prompt(text: str) -> bool:

    text = text.lower()

    for pattern in BLOCKED_PATTERNS:

        if pattern in text:
            return False

    return True