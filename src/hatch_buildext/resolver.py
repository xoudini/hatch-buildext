import typing as t


if t.TYPE_CHECKING:
    from types import ModuleType


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


class Resolver:
    def __init__(self, root: str, module: "ModuleType") -> None:
        self._root = root
        self._module = module

    @property
    def sources(self) -> t.List[str]:
        if isinstance(self._module, _GetSources):
            return self._module.get_sources(root=self._root)
        return []

    @property
    def include_dirs(self) -> t.List[str]:
        if isinstance(self._module, _GetIncludeDirs):
            return self._module.get_include_dirs(root=self._root)
        return []

    @property
    def library_dirs(self) -> t.List[str]:
        if isinstance(self._module, _GetLibraryDirs):
            return self._module.get_library_dirs(root=self._root)
        return []

    @property
    def libraries(self) -> t.List[str]:
        if isinstance(self._module, _GetLibraries):
            return self._module.get_libraries(root=self._root)
        return []

    @property
    def extra_compile_args(self) -> t.List[str]:
        if isinstance(self._module, _GetExtraCompileArgs):
            return self._module.get_extra_compile_args(root=self._root)
        return []

    @property
    def extra_link_args(self) -> t.List[str]:
        if isinstance(self._module, _GetExtraLinkArgs):
            return self._module.get_extra_link_args(root=self._root)
        return []
