import os
import typing as t


if t.TYPE_CHECKING:
    from typing_extensions import Self


class Macro(t.NamedTuple):
    """
    A macro definition to pass to the compiler.

    Macro definitions come in two forms: key-value pairs and lone keys.
    For instance, a tuple `("FOO", "BAR")` will take the form `-DFOO="BAR"`,
    whereas a lone key `("BAZ", None)` will become `-DBAZ`.

    This is equivalent to `#define FOO BAR` and `#define BAZ`, respectively.
    """

    name: str
    value: t.Optional[str] = None

    @classmethod
    def fromenv(cls, key: str) -> "Self":
        return cls(name=key, value=os.environ[key])
