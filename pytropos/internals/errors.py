"""
This module defines what a typing error contains. Any error (or warning) found at
typechecking should be added either to `errors` or `warnings`.
"""

from .miscelaneous import Pos, Singleton

from typing import Optional
from typing import List, Tuple  # noqa: F401
import typing as ty  # noqa: F401

__all__ = ['TypeCheckLogger']


WarningType = str

# Warning scheme:
# F___ : Internal failure
# W0__ : Builtin warning, something may fail
# E0__ : Builtin error, the operation will fail
# W2__ : A warning on an attribute that doesn't exists
# W3__ : A warning that is not builtin but useful in some cases
# W5__ : A warning with some external library (user defined)
# E5__ : Error with some external library (user defined)
# NOTSUPPORTEDYET: Error when some characterist of Python is not yet supported
# NOIDEA : Error not yet classified

# Table of known errors:
# *Deprecated
# F001: Sorry! Pytropos doesn't support calling append with a starred variable
# F002: Store: ----

# W001*: Weird return value: Expected int or float but got ...
# E001: ZeroDivisionError
# E002: ValueError
# E003: OverflowError
# E009: TypeError: unsopported operand type(s)
# E010: TypeError: __bool__ should return bool, returned ___
# E011: AttributeError: 'list' object attribute 'append' is read-only
# E012: AttributeError: 'list' object has no attribute 'append'
# E013: AttributeError: '----'
# E014: TypeError: fun() takes ... arguments (N given)
# E015: TypeError: '---' object is not subscriptable
# E016: TypeError: '---' object is not callable
# E017: TypeError: ---- indices must be integers or slices, not ---
# E018: TypeError: ----- index out of range
# E019: TypeError: '-----' object doesn't support item deletion
# E020: TypeError: '-----' object does not support item assignment
# E021: TypeError: '---' is an invalid keyword argument for -------()
# E022: TypeError: ---() argument must be ---, not '---'

# W201: Global variable not set
# W202: Local variable not set
# W203: Non-local variable not set
# W204: No attribute with that name in module
# W212: Trying to delete already deleted local variable
# W213: Trying to delete already deleted non-local variable

# W501: (numpy) TypeError: '----' object cannot be interpreted as an integer


class TypeCheckLogger(object, metaclass=Singleton):
    def __init__(self) -> None:
        self.warnings = []  # type: List[Tuple[WarningType, str, Optional[Pos]]]

    def new_warning(self, err_code: str, msg: WarningType, pos: Optional[Pos]) -> None:
        self.warnings.append(
            (err_code, msg, pos)
        )

    def __str__(self) -> str:
        return '\n'.join(map(_warning_to_str, self.warnings))


def _warning_to_str(warn: Tuple[WarningType, str, Optional[Pos]]) -> str:
    # TODO(helq): add file to the stuff to the stuff position
    warntype, msg, pos = warn
    if pos is None:
        return "<file-unknown>::: {warntype} {msg}".format(
            warntype=warntype,
            msg=msg
        )
    pos_in_file, file = pos
    if pos_in_file is None:
        return "{file}::: {warntype} {msg}".format(
            file=file,
            warntype=warntype,
            msg=msg
        )
    else:
        lineno, col = pos_in_file
        return "{file}:{lineno}:{col}: {warntype} {msg}".format(
            file=file,
            lineno=lineno,
            col=col,
            warntype=warntype,
            msg=msg
        )
