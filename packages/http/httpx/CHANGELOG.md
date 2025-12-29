# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.9.8](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.9.7...microsoft-kiota-http-v1.9.8) (2025-12-29)


### Miscellaneous Chores

* **microsoft-kiota-http:** Synchronize microsoft-kiota versions

## [1.9.7](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.9.6...microsoft-kiota-http-v1.9.7) (2025-09-09)


### Miscellaneous Chores

* **microsoft-kiota-http:** Synchronize microsoft-kiota versions

## [1.9.6](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.9.5...microsoft-kiota-http-v1.9.6) (2025-08-21)


### Bug Fixes

* ensures BaseMiddleware always creates a new span instead of returning the current span ([8cf1771](https://github.com/microsoft/kiota-python/commit/8cf17717d0e5cd2172461c5c3c4f26c518abd8dc))
* ensures BaseMiddleware creates a new span instead of returning the current span ([8ad6559](https://github.com/microsoft/kiota-python/commit/8ad65594525d7eb45e5b4e48702c22aa325a53bc))

## [1.9.5](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.9.4...microsoft-kiota-http-v1.9.5) (2025-07-18)


### Bug Fixes

* use asyncio.sleep for non-blocking delay in RetryHandler ([6fa6ca5](https://github.com/microsoft/kiota-python/commit/6fa6ca57ba73988c86e7db4378a50b240e928a29))
* use asyncio.sleep for non-blocking delay in RetryHandler ([93f409d](https://github.com/microsoft/kiota-python/commit/93f409d4dae5800e4b88bb40d8a33977c3b7fe3a))

## [1.9.4](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.9.3...microsoft-kiota-http-v1.9.4) (2025-06-27)


### Bug Fixes

* grab the first value if the server response contains a comma ([#482](https://github.com/microsoft/kiota-python/issues/482)) ([dc32a10](https://github.com/microsoft/kiota-python/commit/dc32a10e03e32e8bb5b1913724ae8c50d250fac4))
* only use base_uri from http client ([b5e2fd1](https://github.com/microsoft/kiota-python/commit/b5e2fd12a148d8a29eecfaeaa58c465584e34395))
* only use base_uri from http client ([9b0ec30](https://github.com/microsoft/kiota-python/commit/9b0ec300fa765906465333211ba0bcee1af4b838))

## [1.9.3](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.9.2...microsoft-kiota-http-v1.9.3) (2025-03-24)


### Miscellaneous Chores

* **microsoft-kiota-http:** Synchronize microsoft-kiota versions

## [1.9.2](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.9.1...microsoft-kiota-http-v1.9.2) (2025-02-06)


### Bug Fixes

* return error response if CAE claims are not present in WWW-Authenticate header ([068a92f](https://github.com/microsoft/kiota-python/commit/068a92fe1bb765fce7ef9d05a9e047eb6ee613f9))
* return error response if CAE claims are not present in WWW-Authenticate header ([b86e347](https://github.com/microsoft/kiota-python/commit/b86e347609f64c2a1c69e618bd2cb81d3f91a063))

## [1.9.1](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.9.0...microsoft-kiota-http-v1.9.1) (2025-01-29)


### Bug Fixes

* removes the urllib3 extraneous dependency ([a0ad6d5](https://github.com/microsoft/kiota-python/pull/458/commits/a0ad6d5044a6bd6a184257fb99b382babcce51f0))
* ensure 304 status code does not result in an error ([1b0d8ac](https://github.com/microsoft/kiota-python/commit/1b0d8ac8257ae57d5fd21e803282e61fbf0614f5))
* use the httpx client base url when available ([e0b0421](https://github.com/microsoft/kiota-python/commit/e0b0421188d8e0e3cc05b1844288f12a3eab28c0))

## [1.9.0](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.8.0...microsoft-kiota-http-v1.9.0) (2025-01-20)


### Features

* adds support for python 13 ([f16ca00](https://github.com/microsoft/kiota-python/commit/f16ca0048b2408f3fe008f78afac3c67dd4a056d))
* adds support for python 13 ([0b49df0](https://github.com/microsoft/kiota-python/commit/0b49df04c0885d233044bd34affe3356af798fba))

## [1.8.0](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.7.1...microsoft-kiota-http-v1.8.0) (2025-01-17)


### Miscellaneous Chores

* **microsoft-kiota-http:** Synchronize microsoft-kiota versions

## [1.7.1](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.7.0...microsoft-kiota-http-v1.7.1) (2025-01-15)


### Miscellaneous Chores

* **microsoft-kiota-http:** Synchronize microsoft-kiota versions

## [1.7.0](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.6.8...microsoft-kiota-http-v1.7.0) (2025-01-13)


### Features

* drop support for python 3.8 ([63e157b](https://github.com/microsoft/kiota-python/commit/63e157b2f90d92e360e94670fdaf01095f81e5c8))
* drop support for python 3.8 ([59f284b](https://github.com/microsoft/kiota-python/commit/59f284bb4dff90e468a97c15f2b9bba2fde529db))

## [1.6.8](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.6.7...microsoft-kiota-http-v1.6.8) (2025-01-02)


### Bug Fixes

* opentelemetry warning ([6909e86](https://github.com/microsoft/kiota-python/commit/6909e86d9df2e496107f414ebeb7ff1dc8a8de38))
* opentelemetry warning ([e2b3ae7](https://github.com/microsoft/kiota-python/commit/e2b3ae7ff81b18fe1250a1d104ed41ca3d5cb897))

## [1.6.7](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.6.6...microsoft-kiota-http-v1.6.7) (2024-12-17)


### Miscellaneous Chores

* **microsoft-kiota-http:** Synchronize microsoft-kiota versions

## [1.6.6](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.6.5...microsoft-kiota-http-v1.6.6) (2024-12-05)


### Bug Fixes

* Regex extracting claims (addressing [#420](https://github.com/microsoft/kiota-python/issues/420)) ([b48a9fb](https://github.com/microsoft/kiota-python/commit/b48a9fbd9edbc4ccfeeba096ea2b6b0a5dfb1ce1))

## [1.6.5](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.6.4...microsoft-kiota-http-v1.6.5) (2024-12-05)


### Bug Fixes

* outdated documentation links ([f298ba2](https://github.com/microsoft/kiota-python/commit/f298ba2cf9d6fa3874bc248873f7270fb9499b7f))

## [1.6.4](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.6.3...microsoft-kiota-http-v1.6.4) (2024-12-04)


### Bug Fixes

* bumps httpx minimum version to avoid confusion with API breaking changes ([bfb5bb7](https://github.com/microsoft/kiota-python/commit/bfb5bb7852af23d84a10e2708e27e24c42f4a3e0))

## [1.6.3](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.6.2...microsoft-kiota-http-v1.6.3) (2024-12-02)


### Bug Fixes

* Ensure calculated retry delay validated against correct maximum value of 180 secs ([886f28e](https://github.com/microsoft/kiota-python/commit/886f28e47e38831c3cb55da2e790d73f81d33181))
* Ensures retry count is incremented based on value in retry-attempt header ([c655fa2](https://github.com/microsoft/kiota-python/commit/c655fa253294bf3b8f65be1b991a93ce0890a46a))
* Fixes retry handler exponential back-off to consider the delay specified in the retry handler option ([fd87c67](https://github.com/microsoft/kiota-python/commit/fd87c67d599add9e59f48db76a23dd367376b3e1))

## [1.6.2](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.6.1...microsoft-kiota-http-v1.6.2) (2024-11-11)


### Miscellaneous Chores

* **microsoft-kiota-http:** Synchronize microsoft-kiota versions

## [1.6.1](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.6.0...microsoft-kiota-http-v1.6.1) (2024-11-09)


### Bug Fixes

* fixes typing issues discovered from github api generation ([92cf4c5](https://github.com/microsoft/kiota-python/commit/92cf4c5a33e67406f8f38d255c1ed990d95a7892))
* fixes typing issues discovered from github api generation ([6e68068](https://github.com/microsoft/kiota-python/commit/6e6806880b1fa0a43d63a97b937461d688e62ea0))
* type information for collection of primitives ([b3afe83](https://github.com/microsoft/kiota-python/commit/b3afe83e8ee979a246ed15d24490f6ac8df546bb))

## [1.6.0](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.5.0...microsoft-kiota-http-v1.6.0) (2024-10-28)


### Miscellaneous Chores

* **microsoft-kiota-http:** Synchronize microsoft-kiota versions

## [1.5.0](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.4.6...microsoft-kiota-http-v1.5.0) (2024-10-22)


### Miscellaneous Chores

* **microsoft-kiota-http:** Synchronize microsoft-kiota versions

## [1.4.6](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.4.5...microsoft-kiota-http-v1.4.6) (2024-10-18)


### Miscellaneous Chores

* **microsoft-kiota-http:** Synchronize microsoft-kiota versions

## [1.4.5](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.4.4...microsoft-kiota-http-v1.4.5) (2024-10-16)


### Miscellaneous Chores

* **microsoft-kiota-http:** Synchronize microsoft-kiota versions

## [1.4.4](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.4.3...microsoft-kiota-http-v1.4.4) (2024-10-16)


### Miscellaneous Chores

* **microsoft-kiota-http:** Synchronize microsoft-kiota versions

## [1.4.3](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-http-v1.4.1...microsoft-kiota-http-v1.4.3) (2024-10-16)


### Bug Fixes

* include licence file in distribution package. ([645af28](https://github.com/microsoft/kiota-python/commit/645af285a6f97848b190c51199fda9f541e9027a))

## [1.4.1](https://github.com/microsoft/kiota-python/compare/v1.4.0...v1.4.1) (2024-10-15)


### Bug Fixes

* include licence file in distribution package. ([645af28](https://github.com/microsoft/kiota-python/commit/645af285a6f97848b190c51199fda9f541e9027a))

## [1.4.0](https://github.com/microsoft/kiota-python/compare/v1.3.4...v1.4.0) (2024-10-14)


### Features

* setup release please. ([5411d15](https://github.com/microsoft/kiota-python/commit/5411d156ef08a623c6a463c09f1215a2b83ce3f0))
* setup release please. ([6842de0](https://github.com/microsoft/kiota-python/commit/6842de04a25552852b514c402b864c871ff2d6c6))


### Bug Fixes

* bumps required open telemetry version ([2b8cee1](https://github.com/microsoft/kiota-python/commit/2b8cee10db7ca87545d18b37d8d60af4474e0dd4))
* bumps required open telemetry version ([7f5bc94](https://github.com/microsoft/kiota-python/commit/7f5bc940ec748ca17c4118e75e81e1efff52642f))

## [1.3.4] - 2024-10-11

### Changed

- Updated HTTP span attributes to comply with updated OpenTelemetry semantic conventions. [#409](https://github.com/microsoft/kiota-http-python/issues/409)

## [1.3.3] - 2024-08-12

### Added

### Changed

- Avoid raising an exception when a relative url is used as redirect location.

## [1.3.2] - 2024-07-09

### Added

### Changed

- Do not use mutable default arguments for HttpxRequestAdapter.[#383](https://github.com/microsoft/kiota-http-python/pull/383)

## [1.3.1] - 2024-02-13

### Added

### Changed

- Bugfix issues with middleware maintaining state across requests.[#281](https://github.com/microsoft/kiota-http-python/issues/281)
- Fix issue with redirect handler not closing old responses.[#299](https://github.com/microsoft/kiota-http-python/issues/299)

## [1.3.0] - 2024-02-08

### Added

- Added support for `XXX` status code error mapping in RequestAdapter.[#280](https://github.com/microsoft/kiota-http-python/issues/280)

### Changed

## [1.2.1] - 2024-01-22

### Added

### Changed

- Fixed bug with redirect handler maintaing `max_redirect` across requests.[#246](https://github.com/microsoft/kiota-http-python/issues/246)

## [1.2.0] - 2023-11-29

### Added

- Added headers inspection handler to allow clients to inspect request and response headers.

### Changed

## [1.1.0] - 2023-11-27

### Added

- Added support for additional status codes.

### Changed

## [1.0.0] - 2023-10-31

### Added

### Changed

- GA release.

## [0.6.3] - 2023-10-19

### Added

- Decoupled uri decoding logic used for Telemetry span naming from logic used for Parameter middleware

## [0.6.2] - 2023-10-19

### Added

- Added support for providing custom client when creating with middleware.

### Changed

- Replace default transport with kiota transport when using custom client with proxy.

## [0.6.1] - 2023-10-17

### Changed

- Ensures only URL query parameter names are decoded by `ParametersNameDecodingHandler`. [#207]

## [0.6.0] - 2023-09-01

### Added

- Added support for continuous access evaluation.

### Changed

## [0.5.0] - 2023-07-27

### Added

- Added a translator method to change a `RequestInformation` object into a HTTPX client request object.
- Enabled backing store support

### Changed

## [0.4.4] - 2023-05-31

### Added

- Added a url replace handler for replacing url segments.

### Changed

## [0.4.3] - 2023-05-16

### Added

### Changed

- Fixes bug in getting content from redirected request.

## [0.4.2] - 2023-05-02

### Added

### Changed

- Includes Response headers in APIException for failed requests.

## [0.4.1] - 2023-03-29

### Added

### Changed

- Fixed bug with mapping when deserializing primitive response types.

## [0.4.0] - 2023-02-06

### Added

- Added the HTTP response status code on APIError class.

### Changed

- Fixed bug with middleware not respecting request options.

## [0.3.0] - 2023-01-20

### Changed

- Enabled configuring of middleware during client creation by passing custom options in call to create with default middleware. [#56](https://github.com/microsoft/kiota-http-python/issues/56)

## [0.2.4] - 2023-01-17

### Changed

- Changes the ResponeHandler parameter in RequestAdapter to be a RequestOption
