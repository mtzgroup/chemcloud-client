# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [unreleased]

## [0.15.0] - 2025-02-25

### Added

- Temporary `._token_refresh_lock` `asyncio.Lock` bound to the new event loop for synchronous request invocations.
- `DELETE` request to the ChemCloud server after successfully receiving `ProgramOutput`.
- Adaptive polling interval to `FutureOutput.get_async()` so that the interval is reset if results are collected.

### Removed

- `_HTTPClient._httpx_timeout`.

## [0.14.0] - 2025-02-20

### Added

- Full async API for `chemcloud`. This enables Jupyter support. All `chemcloud` methods have an `_async` version that can be awaited as follows:

  ```python
  from chemcloud import compute_async

  ...
  output = await compute_async("terachem", prog_inputs)
  ```

## [0.13.3] - 2025-02-19

### Added

- `FutureOutput.save()` and `FutureOutput.open()` methods to serialize futures to disks and then open the later for retrieval.

### Changed

- `FutureOutput.single_input` to `.return_single_output`.

## [0.13.2] - 2025-02-18

### Added

- `FutureOutput.single_input` so that list of len 1 submitted to `compute()` still get returned as list. May want to refactor into `FutureOutput` and `FutureOutputs`, but this solution works for a quick fix for today's presentation.

## [0.13.1] - 2025-02-17

### Added

- Usage examples for main `chemcloud` functions.
- Tests for main `chemcloud` functions.
- `queue` can be passed to `configure_client()` or `CCClient()` to specify that all calculations should be submitted to a particular queue.

### Changed

- `ProgramOutput` objects are removed from the `FutureOutput.output` list as they are returned by `.as_completed()` to reduce memory footprint for collecting large batches of results.

## [0.13.0] - 2025-02-16

### Added

- High level `compute()` interface for doing calculations without needing to first instantiate a client.
- More complete `TaskStatus` enum.
- Parallel task submission and retrieval with ChemCloud server via asynchronous coroutines.
- `asyncio.Lock()` to auth requests so that token refreshes are not duplicated by multiple coroutines.
- `.save()` and `.open()` methods to FutureOutput to serialize to/from disk.

### Changed

- Refactored `CCClient`, `_RequestsClient` and `FutureOutput` to have cleaner interface and more clearly defined roles.
- `CCClient.configure()` renamed to `.setup_profile()` to improve clarity and reserve the term `configure` for the new `configure_client` function.
- `compute()` and `client.compute()` are now synchronous by default. If end users want to run calculations asynchronously and have a future object returned pass `return_future=True`.
- `_RequestsClient` is entirely `async` now with a `.run_parallel_requests()` method that can be used for synchronous tasks.
- Lists of `ProgramInput` objects submitted to `CCClient.compute()` are now submitted individually (and concurrently) rather than as a batched, single request. This will prevent the server from having to retrieve large batch calculations which occasionally fills server memory and crashes it.
- `_HTTPClient` and updated requests methods to reuse these clients across requests rather than creating a new connection for each request. This enables connection pooling and reuse of `TCP/SSL` connections, greatly speeding up requests and lowering server load.
- Refactored and renamed methods on `_HTTPClient` for clarity and maintainability.
- Updated documentation to use new `compute()` API instead of instantiating a `client`.

### Removed

- `TaskStatus.complete`. `TaskStatus` has been expanded to mirror celery's states.
- `FutureOutputGroup` in favor of a single `FutureResult` object that can handle both single tasks and arrays of tasks.
- Convenience types defined in `models`.

## [0.12.5] - 2025-02-12

### Fixed

- Retry logic for `httpx.RequestError` now correctly raises an exception after `max_attempts`. Requests that fail due to sporadic connection/network issues will now be retried up to `max_attempts` times.

### Changed

- Removed retry logic for 4xx and 5xx errors.

## [0.12.4] - 2025-02-11

### Added

- Retry requests for 4xx and 5xx status codes. This is a short term fix for the sporadic 500 errors related to `LookupError: unknown encoding: idna` on the server.

## [0.12.3] - 2025-02-10

### Added

- Retry loop for HTTP requests to handle ssl handshake errors or other non-HTTP status code errors.

## [0.12.2] - 2025-02-07

### Changed

- Loosened dependency specifications for `qcio` and `httpx`.

## [0.12.1] - 2024-09-11

### Changed

- Using `FutureOutput` for arrays of inputs of length 1.
- Updated to Python 3.9 typing syntax.

## [0.12.0] - 2024-08-06

### Changed

- Removed `black` and `isort` in favor for `ruff`

### Updated

- 🚨 `python` (`>=3.8` -> `>=3.9`)
- `tomli` (`^1.0` -> `^2.0`)
- `httpx` (`^0.23.1` -> `^0.27`)
- `ruff` (`^0.0287` -> `^0.5`)
- `pytest-httpx` (`<0.23.0` -> `>=0.23.0`)
- `format.sh` script dropped `black` and `isort`.

## [0.11.1] - 2024-07-19

### Changed

- Updated to [qcio 0.11.](https://github.com/coltonbh/qcio/blob/master/CHANGELOG.md#0110---2024-07-19).

## [0.11.0] - 2024-07-12

### Changed

Updated qcio (0.10.1 -> 0.10.2). `Structure.ids` -> `Structure.identifiers`

## [0.10.1] - 2024-07-11

### Added

- `py.typed` file for type checking in projects that depend upon `chemcloud`.

## [0.10.0] - 2024-07-10

### Changed

- Updated to `qcio 0.10.1` which uses `Structure` instead of `Molecule`.

## [0.9.0] - 2024-06-14

### Changed

- Upgraded to `qcio` Generics data structures.
- Upgraded `black` from `^23.0.0` to `^24.0.0`.
- Renamed `collect_wavefucntion` kwarg to `CCClient.compute(...)` to `collect_wfn`.
- Updated the response returned by ChemCloud server to have attributes `status` and `program_output` from `state` and `results`.
- Rebuilt documentation to reflect new `qcio` Generics and renamed kwargs.

## [0.8.3] - 2023-10-20

### Changed

- Updated GitHub actions to run on `pull_request` in addition to `push`.
- Migrated dependency `uiri/toml` to `hukkin/tomli` (Python < 3.11) or the built-in `tomllib` (Python >= 3.11)
- Updated GitHub actions to test against both Python 3.8 and Python 3.11

## [0.8.2] - 2023-09-25

### Changed

- Removed `pydantic==2.4.0` from supported versions due to immediate bug upon this release. When trying to import `CCClient` a reference count error appears to trigger a `KeyError`. Bugs are being tracked here: https://github.com/pydantic/pydantic/issues/7617.

## [0.8.1] - 2023-09-20

### Changed

- Updated to `qcio>=0.7.0` to account for renaming of `DualProgramArgs` to `SubProgramArgs`.

## [0.8.0] - 2023-09-19

### Changed

- `FutureResult` objects now called `FutureOutput` to keep in harmony with `qcio` nomenclature.
- Documentation rewritten to capture API changes with `qcio` and `qcop`.
- `/examples` scripts instantiate a `Molecule` directly rather than opening `h2o.xyz` so that code examples can be run directly from the documentation website.
- All `mkdocs` and associated documentation packages updated to the latest versions.

## [0.7.0] - 2023-09-08

### Changed

- Dropped `QCElemental` in favor of `qcio`.
- Updated client to work with `v2` of the ChemCloud server using `qcio`.
- Updated DevOps stack to be in harmony with other qc\* packages (`poetry`, `GitHub Actions`, `pre-commit`, etc).
- Updated from pydantic `v1` -> `v2`, added `pydantic-settings` to dependencies.
- Changed settings `chemcloud_default_credentials_profile` to `chemcloud_credentials_profile`.
- Updated a few names from `result` to `output` to be more in harmony with `qcio` nomenclature.

### Added

- Publish to pypi from GitHub actions.

## [0.6.2] - 2022-12-27

### Changed

- Updated `qcelemental==0.24.0 -> 0.25.1`

## [0.6.1] - 2022-07-19

### Changed

- Pegged `qcelemental` to version `0.24.0` since `0.25.0` introduces breaking changes. Need to keep this version in sync with `ChemCloud` server version.

## [0.6.0] - 2022-07-19

### Changed

- Updated project name from `qccloud` to `chemcloud`

## [0.5.0] - 2022-07-15

### Changed

- Updated project name from `tccloud` to `qccloud`

## [0.4.1] - 2022-05-07

### Changed

- Upped the default timeout on http reads from 5.0s -> 20.0s.

## [0.4.0] - 2022-4-02

### Added

- `to_file()` and `from_file()` methods to easily save compute job ids for later retrieval.

### Changed

- Simplified management of task ids between client and server. Only need to send a single id to server even if a batch computation was initiated.

### Removed

- Support for Python3.6. Python3.6 end-of-lif'ed December 23, 2021.

## [0.3.1] - 2022-03-27

### Added

- Decode b64 encoded data returned from server in `AtomicResult.extra['tcfe:keywords']`

### Changed

- Updated `config.settings.tcfe_config_kwargs = "tcfe:config` -> `config.settings.tcfe_keywords = "tcfe:keywords`

## [0.3.0] - 2022-03-26

### Added

- Support for `AtomicInput.protocols.native_files`. User can now request QC package specific files generated during a computation.
- Added support for TeraChem-specific `native_files`. c0/ca0/cb0 bytes files (or any bytes data) placed in `AtomicInput.extras['tcfe:keywords']` will be automatically base64 encoded and sent to the server. The enables seeding computations with a wave function as an initial guess.
- Base64 encoded `native_files` returned from server will be automatically decoded to bytes.

## [0.2.4] - 2021-06-07

### Added

- Private compute queues to `compute()` and `compute_procedure()`

## [0.2.3] - 2021-06-04

### Added

- Batch compute for both `compute()` and `compute_procedure()` methods
- `FutureResultGroup` for batch computations

### Changed

- Added `pydantic` `BaseModel` as base for `FutureResult` objects.

## [0.2.2] - 2021-05-21

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

[unreleased]: https://github.com/mtzgroup/chemcloud-client/compare/0.15.0...HEAD
[0.15.0]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.15.0
[0.14.0]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.14.0
[0.13.3]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.13.3
[0.13.2]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.13.2
[0.13.1]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.13.1
[0.13.0]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.13.0
[0.12.5]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.12.5
[0.12.4]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.12.4
[0.12.3]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.12.3
[0.12.2]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.12.2
[0.12.1]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.12.1
[0.12.0]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.12.0
[0.11.1]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.11.1
[0.11.0]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.11.0
[0.10.1]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.10.1
[0.10.0]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.10.0
[0.9.0]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.9.0
[0.8.3]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.8.3
[0.8.2]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.8.2
[0.8.1]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.8.1
[0.8.0]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.8.0
[0.7.0]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.7.0
[0.6.2]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.6.2
[0.6.1]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.6.1
[0.6.0]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.6.0
[0.5.0]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.5.0
[0.4.1]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.4.1
[0.4.0]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.4.0
[0.3.1]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.3.1
[0.3.0]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.3.0
[0.2.4]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.2.4
[0.2.3]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.2.3
[0.2.2]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.2.2
[0.2.1]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.2.1
[0.2.0]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.2.0
[0.1.1]: https://github.com/mtzgroup/chemcloud-client/releases/tag/0.1.1
