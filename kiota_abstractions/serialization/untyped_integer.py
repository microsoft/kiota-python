from .untyped_node import UntypedNode

class UntypedInteger(UntypedNode):
    """
    Represents an untyped node with integer value.
    """
    
    def __init__(self, value: int) -> None:
        """
        Creates a new instance of UntypedInteger.

        Args:
            value (bool): The integer value associated with the node.
        """
        if not isinstance(value, int):
            raise TypeError("Value of UntypedInteger must be of type int")
        self.__value = value

    def get_value(self) -> int:
        """
        Gets the value associated with untyped integer node.

        Returns:
            The value associated with untyped integer node.
        """
        return self.__value