# from functools import partial
# import sys

from typing import Any

verbosity = 0


def dprint(*args: Any, verb: int = 0, **kargs: Any) -> None:
    if verb <= verbosity:
        print(*args, **kargs)


# TODO(helq): use sys.stderr for derror. The major problem of doing this is that pytest
# doesn't give me any error at all!!! ie, `capsys.readouterr().err` doesn't work at all!!!
# REPORT TO PYTEST!
# derror = partial(dprint, file=sys.stderr)
derror = dprint
