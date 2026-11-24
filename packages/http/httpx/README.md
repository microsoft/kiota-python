# Microsoft Kiota HTTP library

[![PyPI version](https://badge.fury.io/py/microsoft-kiota-http.svg)](https://badge.fury.io/py/microsoft-kiota-http)
[![Downloads](https://pepy.tech/badge/microsoft-kiota-http)](https://pepy.tech/project/microsoft-kiota-http)

The Microsoft Kiota HTTP Library is a python HTTP implementation with HTTPX library.

A [Kiota](https://github.com/microsoft/kiota) generated project will need a reference to a http package to make HTTP requests to an API endpoint.

Read more about Kiota [here](https://github.com/microsoft/kiota/blob/main/README.md).

## Using the Microsoft Kiota HTTP library

In order to use this library, install the package by running:

```cmd
pip install microsoft-kiota-http
```

The default middleware runs in this outbound order: URL replacement, query parameter
name decoding, User-Agent, redirect, retry, headers inspection, and body inspection.
The first three handlers prepare the initial request; redirect targets are not rewritten.
Each redirect hop has its own retry budget, and inspection runs on every attempt.
For a custom pipeline with request compression, put `CompressionHandler` after
`UserAgentHandler` and before `RedirectHandler` and `RetryHandler` so requests can reuse
the compressed body. If a hop rejects the compressed body with HTTP 415, only that
hop is replayed uncompressed with its remaining retry budget. A bodyless redirect
is not replayed. HTTPX handles response decompression.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit <https://cla.opensource.microsoft.com>.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
