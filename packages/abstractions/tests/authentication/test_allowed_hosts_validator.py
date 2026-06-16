import pytest

from kiota_abstractions.authentication.allowed_hosts_validator import AllowedHostsValidator


class TestAllowedHostsValidatorInit:
    def test_creates_with_valid_hosts(self):
        validator = AllowedHostsValidator(["example.com", "api.example.com"])
        assert set(validator.get_allowed_hosts()) == {"example.com", "api.example.com"}

    def test_lowercases_hosts(self):
        validator = AllowedHostsValidator(["Example.COM", "API.Example.com"])
        assert set(validator.get_allowed_hosts()) == {"example.com", "api.example.com"}

    def test_raises_on_non_list(self):
        with pytest.raises(TypeError):
            AllowedHostsValidator("example.com")

    def test_raises_on_http_prefix(self):
        with pytest.raises(ValueError):
            AllowedHostsValidator(["http://example.com"])

    def test_raises_on_https_prefix(self):
        with pytest.raises(ValueError):
            AllowedHostsValidator(["https://example.com"])


class TestIsUrlHostValid:
    def test_returns_false_for_empty_url(self):
        validator = AllowedHostsValidator(["example.com"])
        assert validator.is_url_host_valid("") is False

    def test_returns_false_for_none_url(self):
        validator = AllowedHostsValidator(["example.com"])
        assert validator.is_url_host_valid(None) is False

    def test_returns_true_when_allowed_hosts_empty(self):
        validator = AllowedHostsValidator([])
        assert validator.is_url_host_valid("https://anything.com/path") is True

    def test_returns_true_for_allowed_host(self):
        validator = AllowedHostsValidator(["example.com"])
        assert validator.is_url_host_valid("https://example.com/path") is True

    def test_returns_false_for_disallowed_host(self):
        validator = AllowedHostsValidator(["example.com"])
        assert validator.is_url_host_valid("https://evil.com/path") is False

    def test_host_matching_is_case_insensitive(self):
        validator = AllowedHostsValidator(["example.com"])
        assert validator.is_url_host_valid("https://EXAMPLE.COM/path") is True

    def test_returns_false_for_url_without_scheme(self):
        validator = AllowedHostsValidator(["example.com"])
        assert validator.is_url_host_valid("example.com/path") is False

    def test_returns_false_for_url_without_netloc(self):
        validator = AllowedHostsValidator(["example.com"])
        assert validator.is_url_host_valid("https://") is False

    def test_validates_subdomain_separately(self):
        validator = AllowedHostsValidator(["example.com"])
        assert validator.is_url_host_valid("https://sub.example.com/path") is False

    def test_allows_multiple_valid_hosts(self):
        validator = AllowedHostsValidator(["example.com", "api.example.com"])
        assert validator.is_url_host_valid("https://example.com/path") is True
        assert validator.is_url_host_valid("https://api.example.com/path") is True
        assert validator.is_url_host_valid("https://other.com/path") is False

    def test_handles_url_with_port(self):
        validator = AllowedHostsValidator(["example.com"])
        assert validator.is_url_host_valid("https://example.com:8080/path") is True

    def test_handles_url_with_query_and_fragment(self):
        validator = AllowedHostsValidator(["example.com"])
        assert validator.is_url_host_valid("https://example.com/path?q=1#frag") is True


class TestSetAllowedHosts:
    def test_updates_allowed_hosts(self):
        validator = AllowedHostsValidator(["old.com"])
        validator.set_allowed_hosts(["new.com"])
        assert validator.is_url_host_valid("https://new.com/path") is True
        assert validator.is_url_host_valid("https://old.com/path") is False

    def test_raises_on_non_list(self):
        validator = AllowedHostsValidator(["example.com"])
        with pytest.raises(TypeError):
            validator.set_allowed_hosts("example.com")

    def test_raises_on_http_prefix(self):
        validator = AllowedHostsValidator(["example.com"])
        with pytest.raises(ValueError):
            validator.set_allowed_hosts(["http://example.com"])
