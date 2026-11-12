import re
from datetime import date, datetime

from app.errors import ValidationError

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
URL_RE = re.compile(r"^https?://\S+$")


def require_fields(data, fields):
    missing = [f for f in fields if data.get(f) is None or data.get(f) == ""]
    if missing:
        raise ValidationError(f"Missing required field(s): {', '.join(missing)}")


def validate_email(value):
    if not isinstance(value, str) or not EMAIL_RE.match(value.strip()):
        raise ValidationError("Invalid email format.")
    return value.strip().lower()


def validate_length(value, field_name, max_length, min_length=0):
    if value is None:
        value = ""
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be text.")
    if len(value) < min_length or len(value) > max_length:
        raise ValidationError(
            f"{field_name} must be between {min_length} and {max_length} characters."
        )
    return value


def validate_optional_url(value, field_name):
    if value in (None, ""):
        return None
    if not isinstance(value, str) or not URL_RE.match(value.strip()):
        raise ValidationError(f"{field_name} must be a valid http(s) URL.")
    return value.strip()


def validate_optional_date(value, field_name):
    if value in (None, ""):
        return None
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError) as exc:
        raise ValidationError(
            f"{field_name} must be an ISO date (YYYY-MM-DD)."
        ) from exc
