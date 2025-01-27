# vvm

[![Pypi Status](https://img.shields.io/pypi/v/vvm.svg)](https://pypi.org/project/vvm/) [![Build Status](https://img.shields.io/github/actions/workflow/status/vyperlang/vvm/main.yaml?branch=master)](https://github.com/vyperlang/vvm/actions) [![Coverage Status](https://img.shields.io/codecov/c/github/vyperlang/vvm)](https://codecov.io/gh/vyperlang/vvm)

Vyper version management tool.

## Installation

### via `pip`

```bash
pip install vvm
```

### via `setuptools`

```bash
git clone https://github.com/vyperlang/vvm.git
cd vvm
python3 setup.py install
```

## Quickstart

Use `vvm` to install versions of Vyper:

```python
from vvm import install_vyper

install_vyper(version="0.4.0")
```

**Note**: On macOS with the Apple chips, installing some versions of Vyper may fail if you have not first run this
command:

```bash
softwareupdate --install-rosetta
```

To install Vyper without validating the binary (useful for debugging), you can set `validate=False`.

```python
from vvm import install_vyper

install_vyper(version="0.4.0", validate=False)
```

## Testing

`vvm` is tested on Linux, macOS and Windows with Vyper versions `>=0.1.0-beta.16`.

To run the test suite:

```bash
pytest tests/
```

By default, the test suite installs all available `vyper` versions for your OS. If you only wish to test against already installed versions, include the `--no-install` flag. Use the `--vyper-verions` flag to test against one or more specific versions.

## Contributing

Help is always appreciated! Feel free to open an issue if you find a problem, or a pull request if you've solved an issue.

Please check out our [Contribution Guide](CONTRIBUTING.md) prior to opening a pull request.

## License

This project is licensed under the [MIT license](LICENSE).
