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
        if not isinstance(allowed_hosts, list):
            raise TypeError("Allowed hosts must be a list of strings")

        for host in allowed_hosts:
            if host.startswith("https://") or host.startswith("http://"):
                raise ValueError("Allowed host value cannot contain 'https://' or 'http://' prefix")

        self.allowed_hosts: set[str] = {x.lower() for x in allowed_hosts}

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

        for host in allowed_hosts:
            if host.startswith("https://") or host.startswith("http://"):
                raise ValueError("Allowed host value cannot contain 'https://' or 'http://' prefix")

        self.allowed_hosts = {x.lower() for x in allowed_hosts}

    def is_url_host_valid(self, url: str) -> bool:
        """Checks whether the provided host is valid.

        Args:
            url (str): The url to check.

        Returns:
            bool: [description]
        """
        if not url:
            return False
        if not self.get_allowed_hosts():
            return True
        # Format: urlparse("scheme://netloc/path;parameters?query#fragment")
        # Returns: ParseResult(scheme='scheme', netloc='netloc', path='/path;parameters', params='',
        #    query='query', fragment='fragment')
        o = urlparse(url)
        return all([o.scheme, o.netloc])
