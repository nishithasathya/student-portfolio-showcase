from datetime import date

import pytest

from app.errors import ValidationError
from app.validators import (
    require_fields,
    validate_email,
    validate_length,
    validate_optional_date,
    validate_optional_url,
)


def test_require_fields_passes_when_all_present():
    require_fields({"a": 1, "b": 2}, ["a", "b"])  # does not raise


def test_require_fields_raises_on_missing():
    with pytest.raises(ValidationError):
        require_fields({"a": 1}, ["a", "b"])


@pytest.mark.parametrize(
    "value", ["not-an-email", "missing-at.com", "@missing-local.com", "", None]
)
def test_validate_email_rejects_invalid(value):
    with pytest.raises(ValidationError):
        validate_email(value)


def test_validate_email_normalises_case_and_whitespace():
    assert validate_email("  Owner@Example.COM ") == "owner@example.com"


def test_validate_length_rejects_too_long():
    with pytest.raises(ValidationError):
        validate_length("x" * 10, "field", max_length=5)


def test_validate_length_rejects_too_short():
    with pytest.raises(ValidationError):
        validate_length("", "field", max_length=10, min_length=1)


@pytest.mark.parametrize("value", ["javascript:alert(1)", "ftp://x", "not a url"])
def test_validate_optional_url_rejects_non_http(value):
    with pytest.raises(ValidationError):
        validate_optional_url(value, "field")


def test_validate_optional_url_accepts_http_and_https():
    assert (
        validate_optional_url("https://example.com", "field") == "https://example.com"
    )
    assert validate_optional_url(None, "field") is None


def test_validate_optional_date_rejects_bad_format():
    with pytest.raises(ValidationError):
        validate_optional_date("01-05-2026", "field")


def test_validate_optional_date_accepts_iso_format():
    assert validate_optional_date("2026-05-01", "field") == date(2026, 5, 1)
