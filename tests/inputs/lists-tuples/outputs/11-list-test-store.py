import pytropos.internals.values as pv
from pytropos.internals.values.builtin_values import *
from pytropos.internals.values.python_values.builtin_mutvalues import *
from pytropos.internals.values.python_values import PythonValue as PV

exitcode = 1

store = {
    '_': PV.top(),
    'a': PV(List([pv.list([PV(Int.top())]), PV.top()], size=(1, 2))),
    'b': PV(Int.top()),
    'c': PV(List([PV.top(), PV.top()])),
}
store['c'].val.children[('index', 1)] = store['a']
# similar to c[1] = a
