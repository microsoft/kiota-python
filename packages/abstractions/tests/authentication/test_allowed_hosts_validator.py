import pytest

from kiota_abstractions.authentication.allowed_hosts_validator import AllowedHostsValidator


class TestAllowedHostsValidatorInit:
    def test_creates_with_valid_hosts(self):
        validator = AllowedHostsValidator(["example.com", "api.example.com"])
        assert set(validator.get_allowed_hosts()) == {"example.com", "api.example.com"}

    def test_lowercases_hosts(self):
        validator = AllowedHostsValidator(["Example.COM", "API.Example.com"])
        assert set(validator.get_allowed_hosts()) == {"example.com", "api.example.com"}

    def test_trims_whitespace_from_hosts(self):
        validator = AllowedHostsValidator(["  example.com  ", "  api.example.com "])
        assert set(validator.get_allowed_hosts()) == {"example.com", "api.example.com"}

    def test_raises_on_non_list(self):
        with pytest.raises(TypeError):
            AllowedHostsValidator("example.com")  # type: ignore

    def test_raises_on_non_string_element(self):
        with pytest.raises(TypeError):
            AllowedHostsValidator(["example.com", 123])  # type: ignore

    def test_raises_on_empty_string_entry(self):
        with pytest.raises(ValueError):
            AllowedHostsValidator([""])

    def test_raises_on_whitespace_only_entry(self):
        with pytest.raises(ValueError):
            AllowedHostsValidator(["   "])

    def test_raises_on_mixed_valid_and_blank_entry(self):
        with pytest.raises(ValueError):
            AllowedHostsValidator(["example.com", ""])
        with pytest.raises(ValueError):
            AllowedHostsValidator(["example.com", "   "])

    def test_raises_on_http_prefix(self):
        with pytest.raises(ValueError):
            AllowedHostsValidator(["http://example.com"])

    def test_raises_on_https_prefix(self):
        with pytest.raises(ValueError):
            AllowedHostsValidator(["https://example.com"])

    def test_raises_on_uppercase_prefix(self):
        with pytest.raises(ValueError):
            AllowedHostsValidator(["HTTP://example.com"])
        with pytest.raises(ValueError):
            AllowedHostsValidator(["HTTPS://example.com"])

    def test_raises_on_prefix_with_whitespace(self):
        with pytest.raises(ValueError):
            AllowedHostsValidator(["  http://example.com  "])


class TestIsUrlHostValid:
    def test_returns_false_for_empty_url(self):
        validator = AllowedHostsValidator(["example.com"])
        assert validator.is_url_host_valid("") is False

    def test_returns_false_for_none_url(self):
        validator = AllowedHostsValidator(["example.com"])
        assert validator.is_url_host_valid(None) is False  # type: ignore

    def test_returns_false_for_non_string_url(self):
        validator = AllowedHostsValidator(["example.com"])
        assert validator.is_url_host_valid(123) is False  # type: ignore

    def test_returns_true_when_allowed_hosts_empty(self):
        validator = AllowedHostsValidator([])
        assert validator.is_url_host_valid("https://anything.com/path") is True

    def test_returns_false_for_malformed_url_even_when_allowed_hosts_empty(self):
        validator = AllowedHostsValidator([])
        assert validator.is_url_host_valid("not-a-valid-url") is False
        assert validator.is_url_host_valid("https://") is False

    def test_returns_false_for_unmatched_ipv6_bracket(self):
        validator = AllowedHostsValidator(["example.com"])
        assert validator.is_url_host_valid("https://[example.com/path") is False

        empty_validator = AllowedHostsValidator([])
        assert empty_validator.is_url_host_valid("https://[example.com/path") is False

    def test_returns_false_for_userinfo_even_when_allowed_hosts_empty(self):
        validator = AllowedHostsValidator([])
        assert validator.is_url_host_valid("https://user:password@example.com/path") is False
        assert validator.is_url_host_valid("https://@example.com/path") is False
        assert validator.is_url_host_valid("https://:@example.com/path") is False

    def test_returns_false_for_userinfo_url(self):
        validator = AllowedHostsValidator(["example.com"])
        assert validator.is_url_host_valid("https://user:password@example.com/path") is False
        assert validator.is_url_host_valid("https://user@example.com/path") is False

    def test_returns_false_for_explicitly_empty_userinfo(self):
        validator = AllowedHostsValidator(["example.com"])
        assert validator.is_url_host_valid("https://@example.com/path") is False
        assert validator.is_url_host_valid("https://:@example.com/path") is False

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

    def test_returns_true_for_subdomain_matching_allowed_suffix(self):
        validator = AllowedHostsValidator([".fabric.microsoft.com"])
        assert validator.is_url_host_valid(
            "https://abc.123.graphql.fabric.microsoft.com/path"
        ) is True

    def test_returns_false_for_bare_domain_when_allowed_as_suffix(self):
        validator = AllowedHostsValidator([".fabric.microsoft.com"])
        assert validator.is_url_host_valid("https://fabric.microsoft.com/path") is False

    def test_suffix_host_matching_is_case_insensitive(self):
        validator = AllowedHostsValidator([".Fabric.Microsoft.COM"])
        assert validator.is_url_host_valid("https://ABC.z2c.graphql.fabric.microsoft.com/path") is True

    def test_allows_multiple_valid_hosts(self):
        validator = AllowedHostsValidator(["example.com", "api.example.com", ".fabric.microsoft.com"])
        assert validator.is_url_host_valid("https://example.com/path") is True
        assert validator.is_url_host_valid("https://api.example.com/path") is True
        assert validator.is_url_host_valid("https://other.com/path") is False
        assert validator.is_url_host_valid(
            "https://abc.123.graphql.fabric.microsoft.com/path"
        ) is True

    def test_handles_url_with_port(self):
        validator = AllowedHostsValidator(["example.com"])
        assert validator.is_url_host_valid("https://example.com:8080/path") is True

    def test_handles_url_with_query_and_fragment(self):
        validator = AllowedHostsValidator(["example.com"])
        assert validator.is_url_host_valid("https://example.com/path?q=1#frag") is True

    def test_handles_url_with_whitespace(self):
        validator = AllowedHostsValidator(["example.com"])
        assert validator.is_url_host_valid("  https://example.com/path  ") is True


class TestSetAllowedHosts:
    def test_updates_allowed_hosts(self):
        validator = AllowedHostsValidator(["old.com"])
        validator.set_allowed_hosts(["new.com"])
        assert validator.is_url_host_valid("https://new.com/path") is True
        assert validator.is_url_host_valid("https://old.com/path") is False

    def test_raises_on_non_list(self):
        validator = AllowedHostsValidator(["example.com"])
        with pytest.raises(TypeError):
            validator.set_allowed_hosts("example.com")  # type: ignore

    def test_raises_on_empty_string_entry(self):
        validator = AllowedHostsValidator(["example.com"])
        with pytest.raises(ValueError):
            validator.set_allowed_hosts([""])

    def test_raises_on_whitespace_only_entry(self):
        validator = AllowedHostsValidator(["example.com"])
        with pytest.raises(ValueError):
            validator.set_allowed_hosts(["   "])

    def test_raises_on_http_prefix(self):
        validator = AllowedHostsValidator(["example.com"])
        with pytest.raises(ValueError):
            validator.set_allowed_hosts(["http://example.com"])

    def test_allows_suffix_based_hosts_after_update(self):
        validator = AllowedHostsValidator(["example.com"])
        validator.set_allowed_hosts([".fabric.microsoft.com"])
        assert validator.is_url_host_valid(
            "https://abc.123.graphql.fabric.microsoft.com/path"
        ) is True
