# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.5] - 2023-09-15

### Added

### Changed
- Fix error where updating an attribute of a nested backed model marks all other attributes as changed.

## [0.8.4] - 2023-09-14

### Added

### Changed
- Fix error when instantiating BackedModel using positional and keyword arguments

## [0.8.3] - 2023-09-13

### Added

### Changed
- Fix error representation when APIError class has no error attribute.

## [0.8.2] - 2023-09-13

### Added

### Changed
- Switched from uritemplate to std-uritemplate for URI templating.
- Handles exception thrown when APIError class has no error attribute.

## [0.8.1] - 2023-09-01

### Added
- Added opentelemetry to project dependencies.

### Changed

## [0.8.0] - 2023-08-24

### Added
- Added opentelemetry to support observability.
- Added an additional parameter to authentication methods to carry contextual information.

### Changed

## [0.7.1] - 2023-08-09

### Added

### Changed
- Set the default value for the `is_initialization_completed` parameter in the `InMemoryBackingStore` class to be `False` and use the
`__post_init__` method of backed model to set it to `True`.
- Changed the string representation of the `APIError` class to be more descriptive.

## [0.7.0] - 2023-07-27

### Added
- Added an abstract translator method that should convert a `RequestInformation` object into the native client HTTP request object.
- Enable backing store for Python.

### Changed

## [0.6.0] - 2023-06-27

### Added
- API key authentication provider.

### Changed

## [0.5.5] - 2023-06-26

### Added

### Changed

- Changed BaseRequesBuilder class to be instantiable.
- Renamed RequestConfiguration class to BaseRequestConfiguration.

## [0.5.4] - 2023-06-22

### Added

- Added a base request builder and a request configuration class to reduce the amount of code being generated.

### Changed

## [0.5.2] - 2023-06-05

### Added

### Changed

- Changed Parsable and APIError to dataclasses.
- Added support for merging of object values for intersection types

## [0.5.1] - 2023-04-29

### Added

- Adds the response headers to the APIError class.

### Changed

## [0.5.0] - 2023-02-07

### Added

- Added support for multi-valued request headers.

### Changed


## [0.4.0] - 2023-02-06

### Added

### Changed

- Added a response status code property to the API exception class.

## [0.2.3] - 2023-01-17

### Added

### Changed
- Changes the ResponseHandler parameter in RequestAdapter to be a RequestOption