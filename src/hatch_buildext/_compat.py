import sys


if sys.version_info < (3, 9):

    def removeprefix(value: str, prefix: str) -> str:
        if value.startswith(prefix):
            return value[len(prefix) :]
        return value
else:
    removeprefix = str.removeprefix
