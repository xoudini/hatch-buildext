import contextlib
import sys
import typing as t


@contextlib.contextmanager
def add_to_sys_path(path: str) -> t.Generator[None, None, None]:
    if path in sys.path:
        yield
        return

    sys.path.insert(0, path)

    yield

    with contextlib.suppress(ValueError):
        sys.path.remove(path)
