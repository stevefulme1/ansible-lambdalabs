# Changelog

## [2.1.1] - 2026-05-18

### Security
- API keys in idle_cleanup and cost_tracker scripts are now read from a
  separate key file (`/usr/local/etc/lambda-api-key`, mode 0600) instead
  of being embedded inline in shell scripts written to disk
- SSH private key return value in `ssh_key_generate` module is now
  registered with `no_log_values` to prevent accidental logging
- Added `.gitignore` with standard patterns including secret file exclusions

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
