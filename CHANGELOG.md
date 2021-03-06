# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased]

### Added

### Changed

### Removed

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

[unreleased]: https://github.com/mtzgroup/tccloud/compare/0.2.0...HEAD
[0.2.1]: https://github.com/mtzgroup/tccloud/releases/tag/0.2.1
[0.2.0]: https://github.com/mtzgroup/tccloud/releases/tag/0.2.0
[0.1.1]: https://github.com/mtzgroup/tccloud/releases/tag/0.1.1
[core_decisions.md]: https://github.com/mtzgroup/tccloud/blob/develop/docs/development/core_decisions.md
