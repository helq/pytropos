from functools import partial
import sys

from typing import Any

verbosity = 0


def dprint(*args: Any, verb: int = 0, **kargs: Any) -> None:
    if verb <= verbosity:
        print(*args, **kargs)


derror = partial(dprint, file=sys.stderr)
