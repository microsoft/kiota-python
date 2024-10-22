# Kiota Libraries for Python

The Kiota libraries provide the essential building blocks for Kiota-generated SDKs based on OpenAPI definitions, offering default implementations for serialization, authentication, and HTTP transport. These libraries are necessary for compiling and running any Kiota-generated project.

To learn more about Kiota, visit the [Kiota repository](https://github.com/microsoft/kiota).

## Build Status

[![CI Actions Status](https://github.com/microsoft/kiota-python/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/microsoft/kiota-python/actions)

## Libraries

| Library                                                                   | PyPi Release                                                                                                                                        | Changelog                                                      |
|---------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------|
| [Abstractions](./packages/abstractions/README.md)                         | [![PyPI version](https://badge.fury.io/py/microsoft-kiota-abstractions.svg)](https://badge.fury.io/py/microsoft-kiota-abstractions)                 | [Changelog](./packages/abstractions/CHANGELOG.md)              |
| [Authentication - Azure](./packages/authentication/azure/README.md)       | [![PyPI version](https://badge.fury.io/py/microsoft-kiota-authentication-azure.svg)](https://badge.fury.io/py/microsoft-kiota-authentication-azure) | [Changelog](./packages/authentication/azure/CHANGELOG.md)      |
| [Http - HttpClientLibrary](./packages/http/httpx/README.md)               | [![PyPI version](https://badge.fury.io/py/microsoft-kiota-http.svg)](https://badge.fury.io/py/microsoft-kiota-http)                                 | [Changelog](./packages/http/httpx/CHANGELOG.md)                |
| [Serialization - JSON](./packages/serialization/json/README.md)           | [![PyPI version](https://badge.fury.io/py/microsoft-kiota-serialization-json.svg)](https://badge.fury.io/py/microsoft-kiota-serialization-json)     | [Changelog](./packages/serialization/json/CHANGELOG.md)        |
| [Serialization - FORM](./packages/serialization/form/README.md)           | [![PyPI version](https://badge.fury.io/py/microsoft-kiota-serialization-form.svg)](https://badge.fury.io/pymicrosoft-kiota-serialization-form)      | [Changelog](./packages/serialization/form/CHANGELOG.md)        |
| [Serialization - TEXT](./packages/serialization/text/README.md)           | [![PyPI version](https://badge.fury.io/py/microsoft-kiota-serialization-text.svg)](https://badge.fury.io/py/microsoft-kiota-serialization-text)     | [Changelog](./packages/serialization/text/CHANGELOG.md)        |
| [Serialization - MULTIPART](./packages/serialization/multipart/README.md) | [![PyPI version](https://badge.fury.io/py/microsoft-kiota-serialization-multipart.svg)](https://badge.fury.io/py/microsoft-kiota-multipart)         | [Changelog](./packages/serialization/multipart/CHANGELOG.md)   |
| [Bundle](./packages/bundle/README.md)                                     | [![PyPI version](https://badge.fury.io/py/microsoft-kiota-bundle.svg)](https://badge.fury.io/py/microsoft-kiota-bundle)                             | [Changelog](./packages/bundle/CHANGELOG.md)   |

## Contributing

We welcome contributions and suggestions to this project. Most contributions require agreeing to a Contributor License Agreement (CLA) which ensures that you grant us the rights to use your contribution. For more details, please visit <https://cla.opensource.microsoft.com>.

Upon submitting a pull request, a CLA bot will check whether you need to sign the agreement and will update the PR status accordingly. Follow the bot’s instructions if needed. You only need to sign the CLA once across all Microsoft repositories.

This project adheres to the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information, visit the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any questions or comments.

## Trademarks

This project may include trademarks or logos for certain projects, products, or services. Use of Microsoft trademarks or logos must comply with [Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general). Any usage of Microsoft logos in modified versions of this project must not create confusion or imply endorsement by Microsoft. The use of third-party trademarks is subject to the respective owners' policies.
