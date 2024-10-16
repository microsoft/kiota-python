# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.4](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-serialization-text-v1.4.3...microsoft-kiota-serialization-text-v1.4.4) (2024-10-16)


### Miscellaneous Chores

* **microsoft-kiota-serialization-text:** Synchronize microsoft-kiota versions

## [1.4.3](https://github.com/microsoft/kiota-python/compare/microsoft-kiota-serialization-text-v1.4.1...microsoft-kiota-serialization-text-v1.4.3) (2024-10-16)


### Bug Fixes

* fixed type variable in enum writer method to align to reader methods ([d5ce1ec](https://github.com/microsoft/kiota-python/commit/d5ce1ec226b804dd949a2f3b52d1b0cb042fc062))
* include licence file in distribution package. ([645af28](https://github.com/microsoft/kiota-python/commit/645af285a6f97848b190c51199fda9f541e9027a))

## [1.4.1](https://github.com/microsoft/kiota-python/compare/v1.4.0...v1.4.1) (2024-10-15)


### Bug Fixes

* fixed type variable in enum writer method to align to reader methods ([d5ce1ec](https://github.com/microsoft/kiota-python/commit/d5ce1ec226b804dd949a2f3b52d1b0cb042fc062))
* include licence file in distribution package. ([645af28](https://github.com/microsoft/kiota-python/commit/645af285a6f97848b190c51199fda9f541e9027a))

## [1.4.0](https://github.com/microsoft/kiota-python/compare/v1.3.4...v1.4.0) (2024-10-14)


### Features

* setup release please. ([5411d15](https://github.com/microsoft/kiota-python/commit/5411d156ef08a623c6a463c09f1215a2b83ce3f0))
* setup release please. ([6842de0](https://github.com/microsoft/kiota-python/commit/6842de04a25552852b514c402b864c871ff2d6c6))

## [1.0.0] - 2023-10-31

### Added

### Changed

- GA release.

## [0.3.0] - 2023-10-19

### Added

### Changed

- Changed serialization callback methods to properties.

## [0.2.1] - 2023-06-14

### Added

- Added support for composed types serialization.

### Changed

- Changed writer from array to string to prevent writing of multiple values.
- Fixed bug with serializing enums.
