import typing as t
from hatchling.plugin import hookimpl
from hatch_buildext.plugin import ExtensionBuildHook


@hookimpl
def hatch_register_build_hook() -> t.Type[ExtensionBuildHook]:
    return ExtensionBuildHook
