import functools
import pathlib
import typing as t
import zipfile
from hatchling.builders.wheel import WheelBuilder
from tests._utils import register_hooks


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


# TODO: use ast
def _create_resolver(root: pathlib.Path, module: str) -> None:
    source = """
import glob
import pathlib
import typing as t

def get_sources(root: str) -> t.Sequence[str]:
    _src_dir = pathlib.Path(root).joinpath("src")
    return glob.glob(f"{_src_dir}/**/*.c", recursive=True)

def get_include_dirs(root: str) -> t.Sequence[str]:
    return []

def get_library_dirs(root: str) -> t.Sequence[str]:
    return []

def get_libraries(root: str) -> t.Sequence[str]:
    return []

def get_extra_compile_args(root: str) -> t.Sequence[str]:
    return ["-std=c99"]

def get_extra_link_args(root: str) -> t.Sequence[str]:
    return []
"""

    components = module.split(".")

    path = functools.reduce(pathlib.Path.joinpath, components, root)

    if not path.exists():
        path.mkdir(parents=True)

    path.joinpath("__init__").with_suffix(".py").write_text(source)


def _create_c_sample(directory: pathlib.Path) -> None:
    header = """
#ifndef _spam_h
#define _spam_h

static PyObject * spam_system(PyObject *, PyObject *);

#endif /* _spam_h */
"""
    source = """
#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject *
spam_system(PyObject *self, PyObject *args)
{
    const char *command;
    int sts;

    if (!PyArg_ParseTuple(args, "s", &command))
        return NULL;
    sts = system(command);
    return PyLong_FromLong(sts);
}

static PyMethodDef SpamMethods[] = {
    {"system",  spam_system, METH_VARARGS,
     "Execute a shell command."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static struct PyModuleDef spammodule = {
    PyModuleDef_HEAD_INIT,
    "spam",   /* name of module */
    NULL,     /* module documentation, may be NULL */
    -1,       /* size of per-interpreter state of the module,
                 or -1 if the module keeps state in global variables. */
    SpamMethods
};

PyMODINIT_FUNC
PyInit_spam(void)
{
    return PyModule_Create(&spammodule);
}
"""
    directory.joinpath("simple").with_suffix(".h").write_text(header)
    directory.joinpath("simple").with_suffix(".c").write_text(source)


def _create_module(directory: pathlib.Path) -> None:
    if not directory.exists():
        directory.mkdir(parents=True)

    names = "__init__", "__main__"

    for path in map(directory.joinpath, names):
        path.with_suffix(".py").touch()


# TODO: fix
def test_buildwheels(
    project_dir: pathlib.Path,
    build_dir: pathlib.Path,
    tmp_dir: pathlib.Path,  # noqa: ARG001 # TODO: fix
    wheel_conf: t.Mapping[str, object],  # noqa: ARG001  # TODO: fix
) -> None:
    package = pathlib.Path("src") / "foo"

    _resolver = "example.resolver"

    _create_resolver(root=project_dir, module=_resolver)
    _create_module(project_dir / package)
    _create_c_sample(project_dir / package)

    config: "PyProjectConfig" = {
        "project": {
            "name": "test-project",
            "version": "0.1",
        },
        "build-system": {
            "requires": ["hatchling"],
            "build-backend": "hatchling.build",
        },
        "tool": {
            "hatch": {
                "build": {
                    "targets": {
                        "wheel": {
                            "packages": [str(package)],
                            "hooks": {
                                "buildext": {
                                    "dependencies": [
                                        "hatch-buildext",
                                    ],
                                    "extensions": {
                                        "spam": _resolver,
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
    }

    builder = WheelBuilder(root=str(project_dir), config=dict(config))
    register_hooks(builder=builder)

    gen = builder.build(directory=str(build_dir), versions=["standard"])

    result = pathlib.Path(next(gen))
    assert result.exists()

    with zipfile.ZipFile(result) as archive:
        files = _read_record(config=config, archive=archive)

    assert len(files) == 7
