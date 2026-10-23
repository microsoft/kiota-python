from urllib.parse import urlparse


class AllowedHostsValidator:
    """Maintains a list of valid hosts and allows authentication providers to check whether
    a host is valid before authenticating a request
    """

    def __init__(self, allowed_hosts: list[str]) -> None:
        """Creates a new AllowedHostsValidator object with provided values.

        Args:
            allowed_hosts (list[str]): A list of valid hosts.  If the list is empty, all hosts
            are valid.
        """
        self.set_allowed_hosts(allowed_hosts)

    def get_allowed_hosts(self) -> list[str]:
        """Gets the list of valid hosts.  If the list is empty, all hosts are valid.

        Returns:
            list[str]: A list of valid hosts.  If the list is empty, all hosts are valid.
        """
        return list(self.allowed_hosts)

    def set_allowed_hosts(self, allowed_hosts: list[str]) -> None:
        """Sets the list of valid hosts.  If the list is empty, all hosts are valid.

        Args:
            allowed_hosts (list[str]): A list of valid hosts.  If the list is empty, all hosts
            are valid
        """
        if not isinstance(allowed_hosts, list):
            raise TypeError("Allowed hosts must be a list of strings")

        normalized_hosts: set[str] = set()
        for host in allowed_hosts:
            if not isinstance(host, str):
                raise TypeError("Allowed host value must be a string")
            cleaned_host = host.strip()
            if not cleaned_host:
                raise ValueError("Allowed host value cannot be empty or whitespace only")
            lower_host = cleaned_host.lower()
            if lower_host.startswith("https://") or lower_host.startswith("http://"):
                raise ValueError("Allowed host value cannot contain 'https://' or 'http://' prefix")
            normalized_hosts.add(lower_host)

        self.allowed_hosts: set[str] = normalized_hosts

    def is_url_host_valid(self, url: str) -> bool:
        """Checks whether the provided host is valid.

        Args:
            url (str): The url to check.

        Returns:
            bool: True if the host is valid, False otherwise.
        """
        if not url or not isinstance(url, str) or not url.strip():
            return False
        cleaned_url = url.strip()

        # Format: urlparse("scheme://netloc/path;parameters?query#fragment")
        # Returns: ParseResult(scheme='scheme', netloc='netloc', path='/path;parameters', params='',
        #    query='query', fragment='fragment')
        try:
            o = urlparse(cleaned_url)
        except ValueError:
            return False

        if not (o.scheme and o.netloc
                and o.hostname) or (o.username is not None or o.password is not None):
            return False

        if not self.allowed_hosts:
            return True

        hostname = o.hostname.lower()
        return hostname in self.allowed_hosts or any(
            suffix.startswith(".") and hostname.endswith(suffix) for suffix in self.allowed_hosts
        )
