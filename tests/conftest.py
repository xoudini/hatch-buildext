import pathlib
import tempfile
import typing as t
import pytest


@pytest.fixture
def project_dir() -> t.Generator[pathlib.Path, None, None]:
    with tempfile.TemporaryDirectory() as _name:
        yield pathlib.Path(_name)


@pytest.fixture
def build_dir() -> t.Generator[pathlib.Path, None, None]:
    with tempfile.TemporaryDirectory() as _name:
        yield pathlib.Path(_name)


@pytest.fixture
def tmp_dir() -> t.Generator[pathlib.Path, None, None]:
    with tempfile.TemporaryDirectory() as _name:
        yield pathlib.Path(_name)


@pytest.fixture
def wheel_conf() -> t.Mapping[str, object]:
    return dict()
