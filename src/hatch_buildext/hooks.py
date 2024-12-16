from hatchling.plugin import hookimpl
from hatch_buildext.plugin import ExtensionBuildHook


@hookimpl
def hatch_register_build_hook():
    return ExtensionBuildHook
