from .untyped_node import UntypedNode

class UntypedFloat(UntypedNode):
    """
    Represents an untyped node with float value.
    """

    def __init__(self, value: float) -> None:
        """
        Creates a new instance of UntypedFloat.

        Args:
            value (bool): The float value associated with the node.
        """
        self.__value = value

    def get_value(self) -> float:
        """
        Gets the value associated with untyped float node.

        Returns:
            The value associated with untyped float node.
        """
        return self.__value