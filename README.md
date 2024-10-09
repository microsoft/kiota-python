# Kiota Libraries for python

The Kiota libraries define the basic constructs for Kiota projects needed once an SDK has been generated from an OpenAPI definition and provide default implementations.

A [Kiota](https://github.com/microsoft/kiota) generated project will need a reference to the libraries to build and execute by providing default implementations for serialization, authentication and http transport.

Read more about Kiota [here](https://github.com/microsoft/kiota/blob/main/README.md).

## Build Status

[![CI Actions Status](https://github.com/microsoft/kiota-python/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/microsoft/kiota-python/actions)

## Libraries

| Library                                                                   | Pypi Release                                                                                                                                        | Changelog                                                      |
|---------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------|
| [Abstractions](./packages/abstractions/README.md)                         | [![PyPI version](https://badge.fury.io/py/microsoft-kiota-abstractions.svg)](https://badge.fury.io/py/microsoft-kiota-abstractions)                 | [Changelog](./packages/abstractions/CHANGELOG.md)              |
| [Authentication - Azure](./packages/authentication/azure/README.md)       | [![PyPI version](https://badge.fury.io/py/microsoft-kiota-authentication-azure.svg)](https://badge.fury.io/py/microsoft-kiota-authentication-azure) | [Changelog](./packages/authentication/azure/CHANGELOG.md)      |
| [Http - HttpClientLibrary](./packages/http/httpx/README.md)               | [![PyPI version](https://badge.fury.io/py/microsoft-kiota-http.svg)](https://badge.fury.io/py/microsoft-kiota-http)                                 | [Changelog](./packages/http/httpx/CHANGELOG.md)                |
| [Serialization - JSON](./packages/serialization/json/README.md)           | [![PyPI version](https://badge.fury.io/py/microsoft-kiota-serialization-json.svg)](https://badge.fury.io/py/microsoft-kiota-serialization-json)     | [Changelog](./packages/serialization/json/CHANGELOG.md)        |
| [Serialization - FORM](./packages/serialization/form/README.md)           | [![PyPI version](https://badge.fury.io/py/microsoft-kiota-serialization-form.svg)](https://badge.fury.io/pymicrosoft-kiota-serialization-form)      | [Changelog](./packages/serialization/form/CHANGELOG.md)        |
| [Serialization - TEXT](./packages/serialization/text/README.md)           | [![PyPI version](https://badge.fury.io/py/microsoft-kiota-serialization-text.svg)](https://badge.fury.io/py/microsoft-kiota-serialization-text)     | [Changelog](./packages/serialization/text/CHANGELOG.md)        |
| [Serialization - MULTIPART](./packages/serialization/multipart/README.md) | [![PyPI version](https://badge.fury.io/py/microsoft-kiota-serialization-multipart.svg)](https://badge.fury.io/py/microsoft-kiota-multipart)         | [Changelog](./packages/serialization/multipart/CHANGELOG.md)   |

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
