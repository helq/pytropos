from typing import List

__all__ = ["InternalWarning", "internal_warnings"]


class InternalWarning(object):
    def __init__(self, msg: str) -> None:
        self.msg = msg

    def __repr__(self) -> str:
        return "InternalWarning('"+repr(self.msg)+"')"


internal_warnings: List[InternalWarning] = []
