import contextlib
import glob
import importlib
import itertools
import os
import pathlib
import secrets
import shutil
import tempfile
import typing as t
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


if t.TYPE_CHECKING:
    from types import ModuleType
    from hatch_buildext._types import BuildData


class _Extension(t.NamedTuple):
    name: str
    resolver: str


@t.runtime_checkable
class _GetSources(t.Protocol):
    def get_sources(self, root: str) -> t.Sequence[str]: ...


@t.runtime_checkable
class _GetIncludeDirs(t.Protocol):
    def get_include_dirs(self, root: str) -> t.Sequence[str]: ...


@t.runtime_checkable
class _GetLibraryDirs(t.Protocol):
    def get_library_dirs(self, root: str) -> t.Sequence[str]: ...


@t.runtime_checkable
class _GetLibraries(t.Protocol):
    def get_libraries(self, root: str) -> t.Sequence[str]: ...


@t.runtime_checkable
class _GetExtraCompileArgs(t.Protocol):
    def get_extra_compile_args(self, root: str) -> t.Sequence[str]: ...


@t.runtime_checkable
class _GetExtraLinkArgs(t.Protocol):
    def get_extra_link_args(self, root: str) -> t.Sequence[str]: ...


class ExtensionBuildHook(BuildHookInterface):
    PLUGIN_NAME = "buildext"

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]

        self.__extensions: t.Optional[t.Sequence[_Extension]] = None
        # self.__artifacts: t.MutableSequence[bytes] =

        self.__id = secrets.token_hex(8)

    @contextlib.contextmanager
    def _tmp(self) -> t.Generator[str, None, None]:
        with tempfile.TemporaryDirectory() as tmp:
            yield os.path.realpath(tmp)

    @property
    def _cache(self) -> pathlib.Path:
        return (pathlib.Path(self.root) / ".buildext_cache").absolute()

    @property
    def _build_path(self) -> pathlib.Path:
        return (self._cache / self.__id).absolute()

    @property
    def _artifacts(self) -> t.Iterable[str]:
        # TODO: fix
        artifacts = glob.glob(f"{self._build_path}/**/*.so", recursive=True)

        if not artifacts:
            self.app.display_warning("no artifacts found")

        return artifacts

    @property
    def _force_include(self) -> t.Mapping[str, str]:
        def _stripl(name: str) -> str:
            from hatch_buildext._compat import removeprefix

            return removeprefix(name, str(self._build_path))

        return {a: _stripl(a) for a in self._artifacts}

    @property
    def _extensions(self) -> t.Sequence[_Extension]:
        if self.__extensions is None:
            extensions: t.Mapping[str, object] = self.config.get("extensions", dict())

            def _transform(name: str, resolver: str) -> _Extension:
                return _Extension(name=name, resolver=resolver)

            self.__extensions = list(itertools.starmap(_transform, extensions.items()))

        return self.__extensions

    def _load(self, resolver: str) -> "ModuleType":
        from hatch_buildext._utils import add_to_sys_path

        with add_to_sys_path(path=self.root):
            module = importlib.import_module(resolver)

        return module

    def _get_sources(self, module: "ModuleType") -> t.List[str]:
        if isinstance(module, _GetSources):
            return module.get_sources(root=self.root)
        return []

    def _get_include_dirs(self, module: "ModuleType") -> t.List[str]:
        if isinstance(module, _GetIncludeDirs):
            return module.get_include_dirs(root=self.root)
        return []

    def _get_library_dirs(self, module: "ModuleType") -> t.List[str]:
        if isinstance(module, _GetLibraryDirs):
            return module.get_library_dirs(root=self.root)
        return []

    def _get_libraries(self, module: "ModuleType") -> t.List[str]:
        if isinstance(module, _GetLibraries):
            return module.get_libraries(root=self.root)
        return []

    def _get_extra_compile_args(self, module: "ModuleType") -> t.List[str]:
        if isinstance(module, _GetExtraCompileArgs):
            return module.get_extra_compile_args(root=self.root)
        return []

    def _get_extra_link_args(self, module: "ModuleType") -> t.List[str]:
        if isinstance(module, _GetExtraLinkArgs):
            return module.get_extra_link_args(root=self.root)
        return []

    def _build(self) -> None:
        from setuptools import Distribution, Extension
        from setuptools.command import build_ext

        with self._tmp() as tmp:
            build_temp = os.path.join(tmp, "tmp")
            build_lib = self._build_path

            _extensions: t.List["Extension"] = list()

            for extension in self._extensions:
                module = self._load(resolver=extension.resolver)
                _sources = self._get_sources(module=module)
                _include_dirs = self._get_include_dirs(module=module)
                _library_dirs = self._get_library_dirs(module=module)
                _libraries = self._get_libraries(module=module)
                _extra_compile_args = self._get_extra_compile_args(module=module)
                _extra_link_args = self._get_extra_link_args(module=module)

                _extension = Extension(
                    name=extension.name,
                    sources=_sources,
                    include_dirs=_include_dirs,
                    library_dirs=_library_dirs,
                    libraries=_libraries,
                    runtime_library_dirs=None,
                    extra_compile_args=_extra_compile_args,
                    extra_link_args=_extra_link_args,
                )
                _extensions.append(_extension)

            settings = dict(
                ext_modules=_extensions,
            )
            distribution = Distribution(settings)
            command = build_ext.build_ext(dist=distribution)
            command.initialize_options()
            # TODO: to inplace or not to inplace?
            # command.inplace = True
            command.build_temp = build_temp
            command.build_lib = build_lib
            command.finalize_options()
            command.run()

    def initialize(
        self,
        version: str,
        build_data: "BuildData",  # type: ignore[override]
    ) -> None:
        self.app.display_mini_header(self.PLUGIN_NAME)
        self.app.display_debug("=== initialize ===")
        self.app.display_debug("extensions")
        self.app.display_debug(str(self._extensions), level=1)

        self.app.display_debug(f"{version=}")
        self.app.display_debug(f"{build_data=}")
        self.app.display_debug(f"{self.directory=}")
        self.app.display_debug(f"{self.root=}")
        self.app.display_debug(f"{self.config=}")
        self.app.display_debug(f"{self.target_name=}")

        self._build()

        build_data["artifacts"].extend(self._artifacts)
        build_data["force_include"].update(self._force_include)
        build_data["infer_tag"] = True
        build_data["pure_python"] = False

        self.app.display_debug(str(build_data))

    def finalize(
        self,
        version: str,
        build_data: "BuildData",  # type: ignore[override]
        artifact_path: str,
    ) -> None:
        self.app.display_debug("finalize")
        self.app.display_debug(f"{version=}")
        self.app.display_debug(f"{build_data=}")
        self.app.display_debug(f"{artifact_path=}")

    def clean(self, versions: t.Sequence[str]) -> None:
        self.app.display_debug("clean")
        self.app.display_debug(f"{versions=}")
        if self._cache.exists():
            shutil.rmtree(self._cache)
