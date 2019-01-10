from pytropos.internals.values.builtin_values import *
from pytropos.internals.values.python_values import PythonValue as PV

exitcode = 0

store = {
    'i': PV(Int.top()),
    'j': PV(Int.top()),
}
