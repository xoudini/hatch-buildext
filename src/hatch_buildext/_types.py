import typing as t


if t.TYPE_CHECKING:

    class BuildData(t.TypedDict):
        infer_tag: bool
        pure_python: bool
        artifacts: t.List[str]
        force_include: t.Dict[str, str]
