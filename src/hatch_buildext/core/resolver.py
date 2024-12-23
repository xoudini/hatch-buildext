import typing as t
from collections.abc import Sequence
from hatch_buildext.core.macro import Macro


if t.TYPE_CHECKING:
    from types import ModuleType

    T = t.TypeVar("T")


@t.runtime_checkable
class _GetSources(t.Protocol):
    def get_sources(self, root: str, /) -> t.Sequence[str]: ...


@t.runtime_checkable
class _GetIncludeDirs(t.Protocol):
    def get_include_dirs(self, root: str, /) -> t.Sequence[str]: ...


@t.runtime_checkable
class _GetLibraryDirs(t.Protocol):
    def get_library_dirs(self, root: str, /) -> t.Sequence[str]: ...


@t.runtime_checkable
class _GetLibraries(t.Protocol):
    def get_libraries(self, root: str, /) -> t.Sequence[str]: ...


@t.runtime_checkable
class _GetExtraCompileArgs(t.Protocol):
    def get_extra_compile_args(self, root: str, /) -> t.Sequence[str]: ...


@t.runtime_checkable
class _GetExtraLinkArgs(t.Protocol):
    def get_extra_link_args(self, root: str, /) -> t.Sequence[str]: ...


@t.runtime_checkable
class _GetMacros(t.Protocol):
    def get_macros(self, root: str, /) -> t.Sequence["Macro"]: ...


def _ensure(values: object, check: t.Type["T"]) -> t.List["T"]:
    if not isinstance(values, Sequence):
        raise TypeError(f"{values} not a sequence")

    for x in values:
        if not isinstance(x, check):
            raise TypeError(f"incorrect type {type(x)} for {x}, expected {check}")

    return list(values)


class Resolver:
    def __init__(self, root: str, module: "ModuleType") -> None:
        self._root = root
        self._module = module

    @property
    def sources(self) -> t.List[str]:
        if not isinstance(self._module, _GetSources):
            return []
        return _ensure(values=self._module.get_sources(self._root), check=str)

    @property
    def include_dirs(self) -> t.List[str]:
        if not isinstance(self._module, _GetIncludeDirs):
            return []
        return _ensure(values=self._module.get_include_dirs(self._root), check=str)

    @property
    def library_dirs(self) -> t.List[str]:
        if not isinstance(self._module, _GetLibraryDirs):
            return []
        return _ensure(values=self._module.get_library_dirs(self._root), check=str)

    @property
    def libraries(self) -> t.List[str]:
        if not isinstance(self._module, _GetLibraries):
            return []
        return _ensure(values=self._module.get_libraries(self._root), check=str)

    @property
    def extra_compile_args(self) -> t.List[str]:
        if not isinstance(self._module, _GetExtraCompileArgs):
            return []
        return _ensure(
            values=self._module.get_extra_compile_args(self._root),
            check=str,
        )

    @property
    def extra_link_args(self) -> t.List[str]:
        if not isinstance(self._module, _GetExtraLinkArgs):
            return []
        return _ensure(values=self._module.get_extra_link_args(self._root), check=str)

    @property
    def macros(self) -> t.List[Macro]:
        if not isinstance(self._module, _GetMacros):
            return []
        return _ensure(values=self._module.get_macros(self._root), check=Macro)
