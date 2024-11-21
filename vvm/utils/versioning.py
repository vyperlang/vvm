import itertools
import re
from typing import Any, Optional

from packaging.specifiers import SpecifierSet
from packaging.version import Version

from vvm.exceptions import UnexpectedVersionError
from vvm.install import get_installable_vyper_versions, get_installed_vyper_versions

# Find the first occurence of version specifier in the source code.
# allow for indented comment (as the compiler allows it (as of 0.4.0)).
# might have false positive if a triple quoted string contains a line
# that looks like a version specifier and is before the actual version
# specifier in the code, but this is accepted as it is an unlikely edge case.
_VERSION_RE = re.compile(r"^\s*(?:#\s*(?:@version|pragma\s+version)\s+(.*))", re.MULTILINE)


def detect_version_specifier_set(source_code: str) -> Optional[SpecifierSet]:
    """
    Detect the specifier set given by the pragma version in the source code.

    Arguments
    ---------
    source_code : str
        Source code to detect the specifier set from.

    Returns
    -------
    Optional[SpecifierSet]
        vyper version specifier set, or None if none could be detected.
    """
    match = _VERSION_RE.search(source_code)
    if match is None:
        return None

    version_str = match.group(1)

    # X.Y.Z or vX.Y.Z => ==X.Y.Z, ==vX.Y.Z
    if re.match("[v0-9]", version_str):
        version_str = "==" + version_str
    # adapted from vyper/ast/pre_parse.py at commit c32b9b4c6f0d8
    # partially convert npm to pep440
    # - <0.4.0 contracts with complex npm version range might fail
    # - in versions >=1.0.0, the below conversion will be invalid
    version_str = re.sub("^\\^", "~=", version_str)

    return SpecifierSet(version_str)


def _pick_vyper_version(
    specifier_set: SpecifierSet,
    prereleases: Optional[bool] = None,
    check_installed: bool = True,
    check_installable: bool = True,
) -> Version:
    """
    Pick the latest vyper version that is installed and satisfies the given specifier set.
    If None of the installed versions satisfy the specifier set, pick the latest installable
    version.

    Arguments
    ---------
    specifier_set : SpecifierSet
        Specifier set to pick a version for.
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
        Vyper version that satisfies the specifier set, or None if no version satisfies the set.
    """
    versions = itertools.chain(
        get_installed_vyper_versions() if check_installed else [],
        get_installable_vyper_versions() if check_installable else [],
    )
    if (ret := next(specifier_set.filter(versions, prereleases), None)) is None:
        raise UnexpectedVersionError(
            f"No installable Vyper satisfies the specifier {specifier_set}"
        )
    return ret


def detect_vyper_version_from_source(source_code: str, **kwargs: Any) -> Optional[Version]:
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
    Optional[Version]
        vyper version, or None if no version could be detected.
    """
    specifier_set = detect_version_specifier_set(source_code)
    if specifier_set is None:
        return None
    return _pick_vyper_version(specifier_set, **kwargs)
