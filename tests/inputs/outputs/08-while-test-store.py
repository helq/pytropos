from pytropos.internals.values.builtin_values import *
from pytropos.internals.values.python_values import PythonValue as PV

exitcode = 1

store = {
    'i': PV(Int(10)),
    'j': PV.top(),
}
