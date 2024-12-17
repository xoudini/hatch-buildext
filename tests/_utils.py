import typing as t
from hatch_buildext import hooks as _hooks


if t.TYPE_CHECKING:
    from hatchling.builders.plugin.interface import BuilderInterface


def register_hooks(builder: "BuilderInterface") -> None:
    builder.plugin_manager.manager.register(_hooks)
