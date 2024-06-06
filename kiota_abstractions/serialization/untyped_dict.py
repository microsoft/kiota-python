from .untyped_node import UntypedNode

class UntypedDictionary(UntypedNode):
    """
    Represents an untyped node with dictionary value.
    """

    def __init__(self, value: dict[str:UntypedNode]) -> None:
        """
        Creates a new instance of UntypedDictionary.

        Args:
            value (dict): The key-value pair associated with the node.
        """
        if not isinstance(value, dict):
            if not all(isinstance(key, str) for key in value.keys()):
                raise TypeError("Keys of UntypedDictionary must be of type str")
            if not all(isinstance(value, UntypedNode) for value in value.values()):
                raise TypeError("Values of UntypedDictionary must be of type UntypedNode")
            raise TypeError("Value of UntypedDictionary must be of type dict")
        self.__value = value

    def get_value(self) -> dict[str:UntypedNode]:
        """
        Gets the value associated with untyped dictionary node.

        Returns:
            The value associated with untyped dictionary node.
        """
        return self.__value