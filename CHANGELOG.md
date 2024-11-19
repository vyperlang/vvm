# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased](https://github.com/vyperlang/vvm/)
### Changed
- Update contact information in `CONTRIBUTING.md` ([#17](https://github.com/vyperlang/vvm/pull/17), [#18](https://github.com/vyperlang/vvm/pull/18))
- Update dependencies. Minimum python version is now 3.8 ([#22](https://github.com/vyperlang/vvm/pull/22))
- Add `output_format` argument to `compile_source` and `compile_files` ([#21](https://github.com/vyperlang/vvm/pull/21))
- New public function `detect_vyper_version_from_source` ([#23](https://github.com/vyperlang/vvm/pull/23))
- Fix `combine_json` for versions `>0.3.10` ([#29](https://github.com/vyperlang/vvm/pull/29))

## [0.1.0](https://github.com/vyperlang/vvm/tree/v0.1.0) - 2020-10-07
### Added
- Support for Python 3.9
- Cache version information

## [0.0.2](https://github.com/vyperlang/vvm/tree/v0.0.2) - 2020-08-26
### Fixed
- Ignore `.exe` when handling versions on Windows

## [0.0.1](https://github.com/vyperlang/vvm/tree/v0.0.1) - 2020-08-25
- Initial release
