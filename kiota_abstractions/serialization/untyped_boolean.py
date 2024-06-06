from .untyped_node import UntypedNode

class UntypedBoolean(UntypedNode):
    """
    Represents an untyped node with boolean value.
    """

    def __init__(self, value: bool) -> None:
        """
        Creates a new instance of UntypedBoolean.

        Args:
            value (bool): The boolean value associated with the node.
        """
        if not isinstance(value, bool):
            raise TypeError("Value of UntypedBoolean must be of type bool")
        self.__value = value
    
    def get_value(self) -> bool:
        """
        Gets the value associated with untyped boolean node.

        Returns:
            The value associated with untyped boolean node.
        """
        return self.__value