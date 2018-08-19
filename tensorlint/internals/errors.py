"""
This module defines what a typing error contains. Any error (or warning) found at
typechecking should be added either to `errors` or `warnings`.
"""

from .tools import Pos, Singleton

from typing import Optional
from typing import List, Tuple  # noqa: F401
import typing as ty  # noqa: F401

__all__ = ['TypeCheckLogger']


WarningType = str

# Warning scheme:
# W0__ : Builtin warning, something may fail
# E0__ : Builtin error, the operation will fail
# W5__ : A warning with some external library
# E5__ : Error with some external library
# NOIDEA : Error not yet classified


class TypeCheckLogger(object, metaclass=Singleton):
    def __init__(self) -> None:
        self.warnings = []  # type: List[Tuple[WarningType, str, Optional[Pos]]]

    def new_warning(self, err_code: str, msg: WarningType, pos: Optional[Pos]) -> None:
        self.warnings.append(
            (err_code, msg, pos)
        )
