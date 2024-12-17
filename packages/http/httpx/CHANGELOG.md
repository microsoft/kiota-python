# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
