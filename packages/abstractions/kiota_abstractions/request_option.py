from abc import ABC, abstractmethod


class RequestOption(ABC):
    """Represents a request option
    """

    @staticmethod
    @abstractmethod
    def get_key() -> str:
        """Gets the option key for when adding it to a request. Must be unique

        Returns:
            str: The option key
        """
