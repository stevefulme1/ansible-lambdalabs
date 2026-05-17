# Changelog

## [2.0.0] - 2026-05-17

### Added
- Pagination support (limit/offset) for all _info modules
- Distributed training and job scheduler modules
- Comprehensive README with module index, EDA, roles, and examples
- Comprehensive unit and integration test suites
- Pre-commit and linting configuration (ruff, ansible-lint)

### Fixed
- Trailing blank line in galaxy.yml removed
- ssh_key_names no_log warning suppressed
- GPL headers and author format corrected
- Boilerplate and namespace issues resolved
- CI failures resolved across Python 3.11-3.13
- Unused imports and variables cleaned up

### Changed
- Auto-formatted all modules with ruff

## [1.0.0] - 2026-05-15

### Added
- 35 modules covering Lambda Labs GPU cloud API
- CRUD + info module for every resource type
- Unit tests and CI pipeline
