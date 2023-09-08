from typing import Union

from packaging.version import Version


def to_vyper_version(version: Union[str, Version]) -> Version:
    if not isinstance(version, Version):
        version = Version(version)

    return version
