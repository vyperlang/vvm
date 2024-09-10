import json
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from packaging.specifiers import SpecifierSet, InvalidSpecifier, Specifier
from packaging.version import Version

from vvm import wrapper
from vvm.exceptions import VyperError
from vvm.install import get_executable, get_installed_vyper_versions, get_installable_vyper_versions

_VERSION_RE = re.compile(r"\s*#\s*(?:pragma\s+|@)version\s+([=><^~]*)(\d+\.\d+\.\d+\S*)")

# this is used to convert from the npm-style (before 0.4) to the pypi-style (0.4+)
_SPECIFIER_OVERRIDES = {"^": "~=", "~": ">="}


def get_vyper_version() -> Version:
    """
    Get the version of the active `vyper` binary.

    Returns
    -------
    Version
        vyper version
    """
    vyper_binary = get_executable()
    return wrapper._get_vyper_version(vyper_binary)


def detect_version_specifier(source_code: str) -> Optional[Specifier]:
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


def pick_vyper_version(specifier: Specifier, prereleases: bool | None = None) -> Version:
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

    Returns
    -------
    Version
        Vyper version that satisfies the specifier, or None if no version satisfies the specifier.
    """
    try:
        return next(specifier.filter(get_installed_vyper_versions(), prereleases))
    except StopIteration:
        try:
            return next(specifier.filter(get_installable_vyper_versions(), prereleases))
        except StopIteration:
            raise ValueError(f"No installable Vyper satisfies the specifier {specifier}")


def compile_source(
    source: str,
    base_path: Union[Path, str] = None,
    evm_version: str = None,
    vyper_binary: Union[str, Path] = None,
    vyper_version: Version = None,
    detect_version: bool = False,
) -> Dict:
    """
    Compile a Vyper contract.

    Compilation is handled via the `--combined-json` flag. Depending on the vyper
    version used, some keyword arguments may not be available.

    Arguments
    ---------
    source: str
        Vyper contract to be compiled.
    base_path : Path | str, optional
        Use the given path as the root of the source tree instead of the root
        of the filesystem.
    evm_version: str, optional
        Select the desired EVM version. Valid options depend on the `vyper` version.
    vyper_binary : str | Path, optional
        Path of the `vyper` binary to use. If not given, the currently active
        version is used (as set by `vvm.set_vyper_version`)
    vyper_version: Version, optional
        `vyper` version to use. If not given, the currently active version is used.
        Ignored if `vyper_binary` is also given.
    detect_version: bool, optional
        If True, detect the version from the source code and use that as the
        `vyper_version`. If False, raise a `TypeError` if `vyper_version` is not given.

    Returns
    -------
    Dict
        Compiler output. The source file name is given as `<stdin>`.
    """
    if vyper_version is None:
        if detect_version is not True:
            raise TypeError("detect_version must be True if vyper_version is not given")
        version = detect_version_specifier(source)
        vyper_version = pick_vyper_version(version)

    source_path = tempfile.mkstemp(suffix=".vy", prefix="vyper-", text=True)[1]
    with open(source_path, "w") as fp:
        fp.write(source)

    compiler_data = _compile(
        vyper_binary=vyper_binary,
        vyper_version=vyper_version,
        source_files=[source_path],
        base_path=base_path,
        evm_version=evm_version,
    )

    return {"<stdin>": list(compiler_data.values())[0]}


def compile_files(
    source_files: Union[List, Path, str],
    base_path: Union[Path, str] = None,
    evm_version: str = None,
    vyper_binary: Union[str, Path] = None,
    vyper_version: Version = None,
) -> Dict:
    """
    Compile one or more Vyper source files.

    Compilation is handled via the `--combined-json` flag. Depending on the vyper
    version used, some keyword arguments may not be available.

    Arguments
    ---------
    source_files: List
        Path or list of paths of Vyper source files to be compiled.
    base_path : Path | str, optional
        Use the given path as the root of the source tree instead of the root
        of the filesystem.
    evm_version: str, optional
        Select the desired EVM version. Valid options depend on the `vyper` version.
    vyper_binary : str | Path, optional
        Path of the `vyper` binary to use. If not given, the currently active
        version is used (as set by `vvm.set_vyper_version`)
    vyper_version: Version, optional
        `vyper` version to use. If not given, the currently active version is used.
        Ignored if `vyper_binary` is also given.

    Returns
    -------
    Dict
        Compiler output
    """
    return _compile(
        vyper_binary=vyper_binary,
        vyper_version=vyper_version,
        source_files=source_files,
        base_path=base_path,
        evm_version=evm_version,
    )


def _compile(
    base_path: Union[str, Path, None],
    vyper_binary: Union[str, Path, None],
    vyper_version: Optional[Version],
    **kwargs: Any,
) -> Dict:

    if vyper_binary is None:
        vyper_binary = get_executable(vyper_version)

    stdoutdata, stderrdata, command, proc = wrapper.vyper_wrapper(
        vyper_binary=vyper_binary, f="combined_json", p=base_path, **kwargs
    )

    return json.loads(stdoutdata)


def compile_standard(
    input_data: Dict,
    base_path: str = None,
    vyper_binary: Union[str, Path] = None,
    vyper_version: Version = None,
) -> Dict:
    """
    Compile Vyper contracts using the JSON-input-output interface.

    See the Vyper documentation for details on the expected JSON input and output formats.

    Arguments
    ---------
    input_data : Dict
        Compiler JSON input.
    base_path : Path | str, optional
        Use the given path as the root of the source tree instead of the root
        of the filesystem.
    vyper_binary : str | Path, optional
        Path of the `vyper` binary to use. If not given, the currently active
        version is used (as set by `vvm.set_vyper_version`)
    vyper_version: Version, optional
        `vyper` version to use. If not given, the currently active version is used.
        Ignored if `vyper_binary` is also given.

    Returns
    -------
    Dict
        Compiler JSON output.
    """

    if vyper_binary is None:
        vyper_binary = get_executable(vyper_version)

    stdoutdata, stderrdata, command, proc = wrapper.vyper_wrapper(
        vyper_binary=vyper_binary, stdin=json.dumps(input_data), standard_json=True, p=base_path
    )

    compiler_output = json.loads(stdoutdata)
    if "errors" in compiler_output:
        has_errors = any(error["severity"] == "error" for error in compiler_output["errors"])
        if has_errors:
            error_message = "\n".join(
                tuple(
                    error.get("formattedMessage") or error["message"]
                    for error in compiler_output["errors"]
                    if error["severity"] == "error"
                )
            )
            raise VyperError(
                error_message,
                command=command,
                return_code=proc.returncode,
                stdin_data=json.dumps(input_data),
                stdout_data=stdoutdata,
                stderr_data=stderrdata,
                error_dict=compiler_output["errors"],
            )
    return compiler_output
