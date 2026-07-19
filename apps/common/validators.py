
import re
from rest_framework import serializers

EMAIL_RE = re.compile(r'^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$')
PASSWORD_RE = re.compile(r'^(?=.*[A-Za-z])(?=.*\d).{8,}$')          # >=8 chars, 1 letter, 1 digit
ACCESSION_RE = re.compile(r'^AV-\d{4,}$')                            # e.g. AV-1001
LOAN_ID_RE = re.compile(r'^LN-\d{4,}$')                              # e.g. LN-3041
CURATOR_ID_RE = re.compile(r'^CUR-\d{3,}$')                          # e.g. CUR-001
PHONE_RE = re.compile(r'^\+?\d{10,13}$')


def validate_email_format(value: str) -> str:
    if not value or not EMAIL_RE.match(value.strip()):
        raise serializers.ValidationError('Enter a valid email address, e.g. name@example.com.')
    return value.strip().lower()


def validate_password_strength(value: str) -> str:
    if not value or not PASSWORD_RE.match(value):
        raise serializers.ValidationError(
            'Password must be at least 8 characters long and include at least one letter and one digit.'
        )
    return value


def validate_accession_format(value: str) -> str:
    if not ACCESSION_RE.match(value or ''):
        raise serializers.ValidationError('Accession number must look like AV-1001.')
    return value


def sanitize_search_term(term: str | None) -> str:
    """Escape special regex characters in user input before it is used
    inside a MongoDB $regex filter."""
    return re.escape((term or '').strip())


def extract_numeric_suffix(value: str, prefix: str) -> int | None:
    """Pull the numeric part out of an id like 'AV-1007' -> 1007.
    Used by the repositories to compute the next auto-generated id."""
    match = re.match(rf'^{re.escape(prefix)}-(\d+)$', value or '')
    return int(match.group(1)) if match else None
