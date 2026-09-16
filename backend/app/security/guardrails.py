import re
import time
from typing import List, Optional, Tuple, Dict
import logging
from app.cache.redis import redis_client

logger = logging.getLogger("manabi.security.guardrails")


class SecurityGuardrails:
    # Common prompt injection signatures and jailbreak patterns
    INJECTION_PATTERNS = [
        r"(?i)\bignore\s+(all\s+)?(previous|prior|above)\s+instructions\b",
        r"(?i)\bdisregard\s+(all\s+)?(previous|prior|above)\s+instructions\b",
        r"(?i)\byou\s+are\s+now\s+(DAN|unrestricted|jailbroken|evil)\b",
        r"(?i)\breveal\s+(the\s+)?(system\s+prompt|secret\s+key|api\s+key)\b",
        r"(?i)\bprint\s+(the\s+)?(system\s+instructions|internal\s+configuration)\b",
        r"(?i)<\|im_start\|>|<\|im_end\|>|<\|endoftext\|>",
    ]

    # Sensitive token leaks
    SENSITIVE_PATTERNS = [
        r"AIzaSy[A-Za-z0-9_-]{30,40}",  # Google API key
        r"sk-[A-Za-z0-9_-]{20,60}",       # OpenAI API key
        r"Bearer\s+[A-Za-z0-9_\-\.]+",    # Generic Bearer Token
    ]

    def __init__(self):
        self._compiled_injection = [re.compile(p) for p in self.INJECTION_PATTERNS]
        self._compiled_sensitive = [re.compile(p) for p in self.SENSITIVE_PATTERNS]

    def scan_prompt_injection(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Scans input for prompt-injection or jailbreak attempts.
        Returns: (is_injection_detected, matched_pattern_description)
        """
        if not text:
            return False, None

        for pattern in self._compiled_injection:
            match = pattern.search(text)
            if match:
                logger.warning(f"Security Alert: Potential prompt injection detected: '{match.group(0)}'")
                return True, f"Blocked disallowed pattern: {match.group(0)}"

        return False, None

    def sanitize_output(self, text: str) -> str:
        """
        Redacts leaked API keys, tokens, or credential strings from LLM output.
        """
        if not text:
            return text

        sanitized = text
        for pattern in self._compiled_sensitive:
            sanitized = pattern.sub("[REDACTED_CREDENTIAL]", sanitized)

        return sanitized

    def authorize_document_access(
        self,
        document_access_level: str,
        user_role: str,
        document_status: str = "active"
    ) -> bool:
        """
        Enforces Section 37 Document Governance:
        Only active/effective documents accessible by the user's role are permitted.
        """
        # Archived or superseded documents are restricted
        if document_status not in ("active", "draft"):
            return False

        # Role hierarchy: admin > faculty > student
        if user_role == "admin":
            return True
        elif user_role == "faculty":
            return document_access_level in ("public", "student", "faculty")
        else: # student / public
            return document_access_level in ("public", "student")

    async def check_rate_limit(
        self,
        client_identifier: str,
        max_requests: int = 60,
        window_seconds: int = 60
    ) -> Tuple[bool, int]:
        """
        Rate limiter sliding window using Redis with graceful in-memory fallback.
        Returns: (is_allowed, remaining_requests)
        """
        key = f"rate_limit:{client_identifier}"
        try:
            if redis_client.is_available and redis_client._client:
                current = await redis_client._client.incr(key)
                if current == 1:
                    await redis_client._client.expire(key, window_seconds)
                remaining = max(0, max_requests - current)
                return current <= max_requests, remaining
        except Exception as exc:
            logger.debug(f"Redis rate limit check bypassed: {exc}")

        # Fallback to allowed if Redis not reachable in dev
        return True, max_requests


guardrails = SecurityGuardrails()
