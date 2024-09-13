#!/usr/bin/python3

import pytest
from packaging.version import Version
from requests import ConnectionError

import vvm


def pytest_addoption(parser):
    parser.addoption(
        "--no-install",
        action="store_true",
        help="Only run vvm tests against already installed vyper versions",
    )
    parser.addoption(
        "--vyper-versions",
        action="store",
        help="Only run tests against a specific version(s) of vyper",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "min_vyper: minimum version of vyper to run test against")
    config.addinivalue_line("markers", "max_vyper: maximum version of vyper to run test against")


def pytest_collection(session):
    global VERSIONS
    if session.config.getoption("--vyper-versions"):
        VERSIONS = [Version(i) for i in session.config.getoption("--vyper-versions").split(",")]
    elif session.config.getoption("--no-install"):
        VERSIONS = vvm.get_installed_vyper_versions()
    else:
        try:
            VERSIONS = vvm.get_installable_vyper_versions()
        except ConnectionError:
            raise pytest.UsageError(
                "ConnectionError while attempting to get vyper versions.\n"
                "Use the --no-install flag to only run tests against already installed versions."
            )
        for version in VERSIONS:
            vvm.install_vyper(version)


# auto-parametrize the vyper_version fixture with all target vyper versions
def pytest_generate_tests(metafunc):
    if "vyper_version" in metafunc.fixturenames:
        versions = VERSIONS.copy()
        for marker in metafunc.definition.iter_markers(name="min_vyper"):
            versions = [i for i in versions if i >= Version(marker.args[0])]
        for marker in metafunc.definition.iter_markers(name="max_vyper"):
            versions = [i for i in versions if i <= Version(marker.args[0])]
        metafunc.parametrize("vyper_version", versions, indirect=True)


@pytest.fixture
def vyper_version(request):
    """
    Run a test against all vyper versions.
    """
    version = request.param
    vvm.set_vyper_version(version)
    return version


@pytest.fixture
def latest_version():
    global VERSIONS
    return VERSIONS[0]


@pytest.fixture
def foo_source(vyper_version):
    visibility = "external" if vyper_version >= Version("0.2.0") else "public"
    interface = "IERC20" if vyper_version >= Version("0.4.0a") else "ERC20"
    import_path = "ethereum.ercs" if vyper_version >= Version("0.4.0a") else "vyper.interfaces"
    pragma_version = "pragma version" if vyper_version >= Version("0.3.8") else "@version"
    yield f"""
#{pragma_version} {vyper_version}
from {import_path} import {interface}

@{visibility}
def foo() -> int128:
    return 13
"""


@pytest.fixture
def foo_path(tmp_path_factory, foo_source, vyper_version):
    source = tmp_path_factory.getbasetemp().joinpath(f"Foo-{vyper_version}.vy")
    if not source.exists():
        with source.open("w") as fp:
            fp.write(foo_source)
    return source


@pytest.fixture
def input_json(vyper_version):
    json = {
        "language": "Vyper",
        "sources": {},
        "settings": {"outputSelection": {"*": {"*": ["evm.bytecode.object"]}}},
    }
    yield json
