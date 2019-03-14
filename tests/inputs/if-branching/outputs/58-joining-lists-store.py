import pytropos.internals.values as pv
from pytropos.internals.values.builtin_values import *
from pytropos.internals.values.python_values import PythonValue as PV

exitcode = 0

store = {
    'either': pv.Top,
    'a': pv.list([]),
    'b': pv.int(),
    'c': pv.list([pv.int(2), pv.int(3)]),
}
