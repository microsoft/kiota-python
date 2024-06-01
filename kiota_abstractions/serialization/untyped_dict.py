from .untyped_node import UntypedNode

class UntypedDictionary(UntypedNode):
    """
    Represents an untyped node with dictionary value.
    """

    def __init__(self, value: dict) -> None:
        """
        Creates a new instance of UntypedDictionary.

        Args:
            value (dict): The key-value pair associated with the node.
        """
        self.__value = value

    def get_value(self) -> dict:
        """
        Gets the value associated with untyped dictionary node.

        Returns:
            The value associated with untyped dictionary node.
        """
        return self.__value