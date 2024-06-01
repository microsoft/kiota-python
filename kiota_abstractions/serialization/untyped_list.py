from .untyped_node import UntypedNode

class UntypedList(UntypedNode):
    """
    Represents an untyped node with list value.
    """

    def __init__(self, value: list) -> None:
        """
        Creates a new instance of UntypedList.

        Args:
            value (bool): The list value associated with the node.
        """
        self.__value = value

    def get_value(self) -> list:
        """
        Gets the value associated with untyped list node.

        Returns:
            The value associated with untyped list node.
        """
        return self.__value