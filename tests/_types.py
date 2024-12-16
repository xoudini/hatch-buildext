import typing as t


class _ProjectConfig(t.TypedDict):
    name: str
    version: str


class _WheelConfig(t.TypedDict):
    packages: t.Sequence[str]


class _TargetConfig(t.TypedDict):
    wheel: _WheelConfig


class _BuildConfig(t.TypedDict):
    targets: _TargetConfig


class _HatchConfig(t.TypedDict):
    build: _BuildConfig


class _ToolConfig(t.TypedDict):
    hatch: _HatchConfig


class PyProjectConfig(t.TypedDict):
    project: _ProjectConfig
    tool: _ToolConfig


_DistFile = t.Literal["RECORD", "METADATA", "WHEEL"]
