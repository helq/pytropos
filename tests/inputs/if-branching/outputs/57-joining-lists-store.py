import pytropos.internals.values as pv
from pytropos.internals.values.builtin_values import *
from pytropos.internals.values.python_values import PythonValue as PV

exitcode = 0

a = pv.list([None, pv.int(2)])
a.val.children['index', 0] = a

store = {
    'either': pv.int(),
    'a': a,
}
