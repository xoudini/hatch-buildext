import typing as t


class BuildData(t.TypedDict):
    infer_tag: bool
    pure_python: bool
    artifacts: t.List[str]
    force_include: t.Dict[str, str]
