import re

class ModerationHandler:
    def __init__(self, config):
        self.banned_words = set(config.get("banned_words", []))
        self.regex_patterns = config.get("regex_patterns", {})
        self.whitelist = set(config.get("whitelist", []))

    def should_timeout(self, user, message):
        lowered = message.lower()
        if user in self.whitelist:
            return None

        for word in self.banned_words:
            if word in lowered:
                return f"Inappropriate language: {word}"

        for pattern, reason in self.regex_patterns.items():
            if re.search(pattern, message, re.IGNORECASE):
                return reason

        return None
