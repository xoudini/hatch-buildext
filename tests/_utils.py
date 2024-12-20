import typing as t
from hatch_buildext import hooks as _hooks


if t.TYPE_CHECKING:
    from hatchling.builders.config import BuilderConfigBound as Config
    from hatchling.builders.plugin.interface import BuilderInterface as Builder
    from hatchling.plugin.manager import PluginManagerBound as PluginManager


def register_hooks(builder: "Builder[Config, PluginManager]") -> None:
    builder.plugin_manager.manager.register(_hooks)
