import itertools
import re
from typing import Optional

from packaging.specifiers import InvalidSpecifier, Specifier, SpecifierSet
from packaging.version import Version

from vvm.exceptions import UnexpectedVersionError
from vvm.install import get_installable_vyper_versions, get_installed_vyper_versions

_VERSION_RE = re.compile(r"\s*#\s*(?:pragma\s+|@)version\s+([=><^~]*)(\d+\.\d+\.\d+\S*)")

# this is used to convert from the npm-style (before 0.4) to the pypi-style (0.4+)
_SPECIFIER_OVERRIDES = {"^": "~=", "~": ">="}


def _detect_version_specifier(source_code: str) -> Optional[Specifier]:
    """
    Detect the version given by the pragma version in the source code.

    Arguments
    ---------
    source_code : str
        Source code to detect the version from.

    Returns
    -------
    str
        vyper version, or None if no version could be detected.
    """
    try:
        match = next(_VERSION_RE.finditer(source_code))
        specifier, version_str = match.groups()
        if specifier in ("~", "^"):
            # convert from npm-style to pypi-style
            if specifier == "^":
                # minor match, remove the patch from the version
                version_str = ".".join(version_str.split(".")[:-1])
            specifier = "~="  # finds compatible versions
        specifier = _SPECIFIER_OVERRIDES.get(specifier, specifier) or "=="
        return Specifier(specifier + version_str)
    except (StopIteration, InvalidSpecifier):
        return None


def _pick_vyper_version(
    specifier: Specifier,
    prereleases: bool | None = None,
    check_installed=True,
    check_installable=True,
) -> Version:
    """
    Pick the latest vyper version that is installed and satisfies the given specifier.
    If None of the installed versions satisfy the specifier, pick the latest installable
    version.

    Arguments
    ---------
    specifier : SpecifierSet
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
    try:
        return next(specifier.filter(versions, prereleases))
    except StopIteration:
        raise UnexpectedVersionError(f"No installable Vyper satisfies the specifier {specifier}")


def detect_vyper_version_from_source(source_code: str, **kwargs) -> Version:
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
    if specifier is None:
        raise UnexpectedVersionError("No version detected in source code")
    return _pick_vyper_version(specifier, **kwargs)
