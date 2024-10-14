from .untyped_node import UntypedNode

class UntypedString(UntypedNode):
    """
    Represents an untyped node with string value.
    """
    
    def __init__(self, value: str) -> None:
        """
        Creates a new instance of UntypedStr.

        Args:
            value (bool): The string value associated with the node.
        """
        if not isinstance(value, str):
            raise TypeError("Value of UntypedStr must be of type str")
        self.__value = value

    def get_value(self) -> str:
        """
        Gets the value associated with untyped string node.

        Returns:
            The value associated with untyped string node.
        """
        return self.__value
