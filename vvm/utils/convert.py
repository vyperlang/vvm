from typing import Union

from packaging.version import Version


def to_vyper_version(version: Union[str, Version]) -> Version:
    if not isinstance(version, Version):
        version = Version(version)

    if not version.pre:
        return version

    if version.pre[0] == "b":
        version.pre = ("beta",) + version.prerelease[1:]

    return version
