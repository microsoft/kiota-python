from __future__ import annotations

import re
from typing import Any, Optional

from .serialization_writer import SerializationWriter
from .serialization_writer_factory import SerializationWriterFactory


class SerializationWriterFactoryRegistry(SerializationWriterFactory):
    """This factory holds a list of all the registered factories for the various types of nodes.
    """
    # List of factories that are registered by content type.
    CONTENT_TYPE_ASSOCIATED_FACTORIES: dict[str, SerializationWriterFactory] = {}

    __instance: Optional[SerializationWriterFactoryRegistry] = None

    def __new__(cls, *args: Any, **kwargs: Any) -> SerializationWriterFactoryRegistry:
        """Default singleton instance of the registry to be used when registring new
        factories that should be available by default.

        Returns:
            [SerializationWriterFactoryRegistry]: Default singleton instance of the class
        """
        if not SerializationWriterFactoryRegistry.__instance:
            SerializationWriterFactoryRegistry.__instance = object.__new__(cls)
        return SerializationWriterFactoryRegistry.__instance

    def get_valid_content_type(self) -> str:
        raise Exception(
            "The registry supports multiple content types. Get the registered factory instead"
        )

    def get_serialization_writer(self, content_type: str) -> SerializationWriter:
        if not content_type:
            raise Exception("Content type cannot be null")

        vendor_specific_content_type = content_type.split(';')[0]
        cleaned_content_type = re.sub(r'[^/]+\+', '', vendor_specific_content_type)
        # Preserve direct exact-key registrations; normal registration uses lowercase keys.
        for candidate in (
            vendor_specific_content_type, vendor_specific_content_type.lower(),
            cleaned_content_type, cleaned_content_type.lower()
        ):
            factory = self.CONTENT_TYPE_ASSOCIATED_FACTORIES.get(candidate)
            if factory:
                dispatch_type = candidate
                if not isinstance(factory, SerializationWriterFactoryRegistry):
                    declared_type = factory.get_valid_content_type()
                    if declared_type.lower() == candidate.lower():
                        dispatch_type = declared_type
                return factory.get_serialization_writer(dispatch_type)

        raise Exception(
            f"Content type {cleaned_content_type} does not have a factory registered"
            "to be serialized"
        )
