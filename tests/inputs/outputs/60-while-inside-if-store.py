import pytropos.internals.values as pv
from pytropos.internals.values.builtin_values import *
from pytropos.internals.values.python_values import PythonValue as PV

exitcode = 0

store = {
    'i': pv.int(10),
    'j': pv.int(1265),
}
