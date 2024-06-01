from .untyped_node import UntypedNode

class UntypedNone(UntypedNode):
    """
    Represents an untyped node with none value.
    """

    def get_value(self) -> None:
        """
        Gets the value associated with untyped none node.

        Returns:
            The value associated with untyped none node.
        """
        return None