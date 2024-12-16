import pathlib
import typing as t
import zipfile
from hatchling.builders.wheel import WheelBuilder


if t.TYPE_CHECKING:
    from tests._types import PyProjectConfig


class _File(t.NamedTuple):
    path: str
    digest: str
    size: int


def _read_record(
    config: "PyProjectConfig",
    archive: zipfile.ZipFile,
) -> t.Sequence[_File]:
    name = config["project"]["name"].replace("-", "_")
    version = config["project"]["version"]
    path = f"{name}-{version}.dist-info/RECORD"
    record = archive.read(path).decode("utf-8")

    def _predicate(part: str) -> t.TypeGuard[str]:
        return not part.startswith(path)

    def _transform(part: str) -> _File:
        path, digest, size = part.split(",")
        return _File(path=path, digest=digest, size=int(size))

    return tuple(map(_transform, filter(_predicate, record.split())))


def _create_module(directory: pathlib.Path) -> None:
    if not directory.exists():
        directory.mkdir(parents=True)

    names = "__init__", "__main__"

    for path in map(directory.joinpath, names):
        path.with_suffix(".py").touch()


def test_buildwheels(
    project_dir: pathlib.Path,
    build_dir: pathlib.Path,
    tmp_dir: pathlib.Path,
    wheel_conf: t.Mapping[str, object],
) -> None:
    package = pathlib.Path("src") / "foo"

    _create_module(project_dir / package)

    config: "PyProjectConfig" = {
        "project": {
            "name": "test-project",
            "version": "0.1",
        },
        "tool": {
            "hatch": {
                "build": {
                    "targets": {
                        "wheel": {
                            "packages": [str(package)],
                        }
                    }
                },
            }
        },
    }

    builder = WheelBuilder(root=str(project_dir), config=config)
    gen = builder.build(directory=str(build_dir), versions=["standard"])

    result = pathlib.Path(next(gen))
    assert result.exists()

    with zipfile.ZipFile(result) as archive:
        files = _read_record(config=config, archive=archive)

        assert len(files) == 4
