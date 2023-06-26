# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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