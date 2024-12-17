import typing as t


_Builder = t.Literal["hatchling"]
_BuildBackend = t.Literal["hatchling.build"]

_BuildSystemConfig = t.TypedDict(
    "_BuildSystemConfig",
    {
        "requires": t.Sequence[_Builder],
        "build-backend": _BuildBackend,
    },
)


class _ProjectConfig(t.TypedDict):
    name: str
    version: str


class _BuildextHookConfig(t.TypedDict):
    dependencies: t.Sequence[t.Union[t.Literal["hatch-buildext"], str]]
    extensions: t.Mapping[str, str]


class _HooksConfig(t.TypedDict):
    buildext: _BuildextHookConfig


class _WheelConfig(t.TypedDict):
    packages: t.Sequence[str]
    hooks: _HooksConfig


class _TargetConfig(t.TypedDict):
    wheel: _WheelConfig


class _BuildConfig(t.TypedDict):
    targets: _TargetConfig


class _HatchConfig(t.TypedDict):
    build: _BuildConfig


class _ToolConfig(t.TypedDict):
    hatch: _HatchConfig


PyProjectConfig = t.TypedDict(
    "PyProjectConfig",
    {
        "build-system": _BuildSystemConfig,
        "project": _ProjectConfig,
        "tool": _ToolConfig,
    },
)


_DistFile = t.Literal["RECORD", "METADATA", "WHEEL"]
