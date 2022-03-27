# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1]

### Added

- Decode b64 encoded data returned from server in `AtomicResult.extra['tcfe:keywords']`

### Changed

- Updated `config.settings.tcfe_config_kwargs = "tcfe:config` -> `config.settings.tcfe_keywords = "tcfe:keywords`

## [0.3.0]

### Added

- Support for `AtomicInput.protocols.native_files`. User can now request QC package specific files generated during a computation.
- Added support for TeraChem-specific `native_files`. c0/ca0/cb0 bytes files (or any bytes data) placed in `AtomicInput.extras['tcfe:keywords']` will be automatically base64 encoded and sent to the server. The enables seeding computations with a wave function as an initial guess.
- Base64 encoded `native_files` returned from server will be automatically decoded to bytes.

## [0.2.4]

### Added

- Private compute queues to `compute()` and `compute_procedure()`

## [0.2.3]

### Added

- Batch compute for both `compute()` and `compute_procedure()` methods
- `FutureResultGroup` for batch computations

### Changed

- Added `pydantic` `BaseModel` as base for `FutureResult` objects.

## [0.2.2]

### Added

- Extended documentation to include a Code Reference section and much more comprehensive documentation of the main objects.
- Added `compute_procedure` to `TCClient` for geometry optimizations.
- Added `TCClient.version` property for quick version checks.

## [0.2.1] - 2021-03-05

### Added

- Changelog
- User documentation
- Website for documentation

## [0.2.0] - 2021-02-26

### Added

- Added `TaskStatus` enum to hold all task statuses.
- Basic documentation on main classes.
- [core_decisions.md] to document thinking behind architectural choices.

### Changed

- `FutureResult.get()` to return either an `AtomicResult` or a `FailedComputation`
- Simplified README.md overview to use dictionaries instead of classes. Results in simpler tutorial with fewer imports.

## [0.1.1] - 2021-01-22

### Added

- `TCClient` that can manage credentials, submit AtomicInput computations, and retrieve AtomicResult output from TeraChem Cloud.
- `_RequestsClient` class that handles all network requests to TeraChem Cloud server
- `FutureResults` object that is created from a `task_id` and can be used to retrieve a result once finished.

[unreleased]: https://github.com/mtzgroup/tccloud/compare/0.3.1...HEAD
[0.3.1]: https://github.com/mtzgroup/tccloud/releases/tag/0.3.1
[0.3.0]: https://github.com/mtzgroup/tccloud/releases/tag/0.3.0
[0.2.4]: https://github.com/mtzgroup/tccloud/releases/tag/0.2.4
[0.2.3]: https://github.com/mtzgroup/tccloud/releases/tag/0.2.3
[0.2.2]: https://github.com/mtzgroup/tccloud/releases/tag/0.2.2
[0.2.1]: https://github.com/mtzgroup/tccloud/releases/tag/0.2.1
[0.2.0]: https://github.com/mtzgroup/tccloud/releases/tag/0.2.0
[0.1.1]: https://github.com/mtzgroup/tccloud/releases/tag/0.1.1
[core_decisions.md]: https://github.com/mtzgroup/tccloud/blob/develop/docs/development/core_decisions.md
