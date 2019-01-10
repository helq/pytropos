from pytropos.internals.values.builtin_values import *
from pytropos.internals.values.python_values import PythonValue as PV

exitcode = 1

store = {
    'a': PV(Int(5)),
    'c': PV(Int(2)),
    'd': PV.top()
}
