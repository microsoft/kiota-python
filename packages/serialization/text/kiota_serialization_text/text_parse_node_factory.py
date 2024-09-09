from kiota_abstractions.serialization import ParseNode, ParseNodeFactory

from .text_parse_node import TextParseNode


class TextParseNodeFactory(ParseNodeFactory):
    """Factory that is used to create TextParseNodes.
    """

    def get_valid_content_type(self) -> str:
        """Returns the content type this factory's parse nodes can deserialize
        Returns:
            str: The content type to be deserialized
        """
        return 'text/plain'

    def get_root_parse_node(self, content_type: str, content: bytes) -> ParseNode:
        """Creates a ParseNode from the given binary stream and content type
        Args:
            content_type (str): The content type of the binary stream
            content (bytes): The array buffer to read from
        Returns:
            ParseNode: A ParseNode that can deserialize the given binary stream
        """
        if not content_type:
            raise TypeError("Content Type cannot be null")
        valid_content_type = self.get_valid_content_type()
        if valid_content_type.casefold() != content_type.casefold():
            raise TypeError(f"Expected {valid_content_type} as content type")

        if not content:
            raise TypeError("Content cannot be null")

        content_as_str = content.decode('utf-8')
        return TextParseNode(content_as_str)
