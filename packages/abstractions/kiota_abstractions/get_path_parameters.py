from typing import Any, Optional, Union

from .request_information import RequestInformation


def get_path_parameters(parameters: Union[dict[str, Any], Optional[str]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    if isinstance(parameters, str):
        result[RequestInformation.RAW_URL_KEY] = parameters
    elif isinstance(parameters, dict):
        for key, val in parameters.items():
            result[key] = val
    return result
