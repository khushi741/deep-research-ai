import pytest
from app.utils.security import validate_url_for_ssrf, is_ip_blocked


def test_localhost_blocked():
    is_safe, msg = validate_url_for_ssrf("http://localhost:8000/admin")
    assert not is_safe
    assert "blocked" in msg.lower() or "localhost" in msg.lower()


def test_loopback_ip_blocked():
    is_safe, msg = validate_url_for_ssrf("http://127.0.0.1/secret")
    assert not is_safe


def test_private_ip_range_blocked():
    is_safe, msg = validate_url_for_ssrf("http://192.168.1.1/router")
    assert not is_safe
    assert "blocked" in msg.lower()


def test_cloud_metadata_blocked():
    # AWS/GCP Metadata endpoint
    is_safe, msg = validate_url_for_ssrf("http://169.254.169.254/latest/meta-data/")
    assert not is_safe


def test_forbidden_scheme_blocked():
    is_safe, msg = validate_url_for_ssrf("file:///etc/passwd")
    assert not is_safe
    assert "scheme" in msg.lower()


def test_safe_public_url():
    is_safe, msg = validate_url_for_ssrf("https://example.com/article")
    assert is_safe
    assert "safe" in msg.lower()
