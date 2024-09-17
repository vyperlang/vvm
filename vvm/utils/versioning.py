import itertools
import re
from typing import Any, Optional

from packaging.specifiers import Specifier
from packaging.version import Version

from vvm.exceptions import UnexpectedVersionError
from vvm.install import get_installable_vyper_versions, get_installed_vyper_versions

_VERSION_RE = re.compile(r"\s*#\s*(?:pragma\s+|@)version\s+([=><^~]*)(\d+\.\d+\.\d+\S*)")


def _detect_version_specifier(source_code: str) -> Specifier:
    """
    Detect the version given by the pragma version in the source code.

    Arguments
    ---------
    source_code : str
        Source code to detect the version from.

    Returns
    -------
    str
        vyper version specifier, or None if none could be detected.
    """
    match = _VERSION_RE.search(source_code)
    if match is None:
        raise UnexpectedVersionError("No version detected in source code")

    specifier, version_str = match.groups()
    if specifier in ("~", "^"):  # convert from npm-style to pypi-style
        if Version(version_str) >= Version("0.4.0"):
            error = "Please use the pypi-style version specifier "
            error += f"for vyper versions >= 0.4.0 (hint: try ~={version_str})"
            raise UnexpectedVersionError(error)
        # for v0.x, both specifiers are equivalent
        specifier = "~="  # finds compatible versions

    if specifier == "":
        specifier = "=="
    return Specifier(specifier + version_str)


def _pick_vyper_version(
    specifier: Specifier,
    prereleases: Optional[bool] = None,
    check_installed: bool = True,
    check_installable: bool = True,
) -> Version:
    """
    Pick the latest vyper version that is installed and satisfies the given specifier.
    If None of the installed versions satisfy the specifier, pick the latest installable
    version.

    Arguments
    ---------
    specifier : Specifier
        Specifier to pick a version for.
    prereleases : bool, optional
        Whether to allow prereleases in the returned iterator. If set to
        ``None`` (the default), it will be intelligently decide whether to allow
        prereleases or not (based on the specifier.prereleases attribute, and
        whether the only versions matching are prereleases).
    check_installed : bool, optional
        Whether to check the installed versions. Defaults to True.
    check_installable : bool, optional
        Whether to check the installable versions. Defaults to True.

    Returns
    -------
    Version
        Vyper version that satisfies the specifier, or None if no version satisfies the specifier.
    """
    versions = itertools.chain(
        get_installed_vyper_versions() if check_installed else [],
        get_installable_vyper_versions() if check_installable else [],
    )
    if (ret := next(specifier.filter(versions, prereleases), None)) is None:
        raise UnexpectedVersionError(f"No installable Vyper satisfies the specifier {specifier}")
    return ret


def detect_vyper_version_from_source(source_code: str, **kwargs: Any) -> Version:
    """
    Detect the version given by the pragma version in the source code.

    Arguments
    ---------
    source_code : str
        Source code to detect the version from.
    kwargs : Any
        Keyword arguments to pass to `pick_vyper_version`.

    Returns
    -------
    Version
        vyper version, or None if no version could be detected.
    """
    specifier = _detect_version_specifier(source_code)
    return _pick_vyper_version(specifier, **kwargs)
