from pytropos.internals.values.builtin_values import *
from pytropos.internals.values.python_values import PythonValue as PV

exitcode = 1

store = {
    '_': PV.top(),
    'c': PV.top(),
    'b': PV.top(),
    'a': PV.top(),
}
