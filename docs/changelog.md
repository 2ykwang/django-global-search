# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.2] - 2025-10-09

### Added

- Add release GitHub Action ([#13](https://github.com/2ykwang/django-global-search/pull/13))
- Add demo project for testing django-global-search ([#12](https://github.com/2ykwang/django-global-search/pull/12))
- Add toggle buttons to collapse/expand app search results ([#11](https://github.com/2ykwang/django-global-search/pull/11))

## [0.1.1] - 2025-10-08

### Added

- Prepare release 0.1.1 ([#10](https://github.com/2ykwang/django-global-search/pull/10))
  - Add sdist build configuration to pyproject.toml
- Add pre-commit config ([#9](https://github.com/2ykwang/django-global-search/pull/9))
- Support i18n ([#7](https://github.com/2ykwang/django-global-search/pull/7))

## [0.1.0] - 2025-10-07

### Added

- Initial release of Django Global Search
- Global search functionality across all registered Django Admin models
- Support for Django Admin's existing `search_fields` configuration
- Multi-AdminSite support with `current_app` parameter
- CI workflow with GitHub Actions
- Tox configuration for testing across multiple Django/Python versions
- Comprehensive test suite with pytest
- ReadTheDocs documentation

### Changed

- Optimize model search with two-step query approach
- Refactor search logic code for better maintainability
- Reduce URL length with app-level model selection

### Fixed

- Fix apply button functionality in search filters
