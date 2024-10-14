from .untyped_node import UntypedNode

class UntypedList(UntypedNode):
    """
    Represents an untyped node with list value.
    """

    def __init__(self, value: list[UntypedNode]) -> None:
        """
        Creates a new instance of UntypedList.

        Args:
            value (bool): The list value associated with the node.
        """
        if not isinstance(value, list):
            if not all(isinstance(value, UntypedNode) for value in value):
                raise TypeError("Values of UntypedList must be of type UntypedNode")
            raise TypeError("Value of UntypedList must be of type list")
        self.__value = value

    def get_value(self) -> list[UntypedNode]:
        """
        Gets the value associated with untyped list node.

        Returns:
            The value associated with untyped list node.
        """
        return self.__value