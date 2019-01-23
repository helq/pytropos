import pytropos.internals.values as pv
from pytropos.internals.values.python_values import PythonValue as PV

exitcode = 1

store = {
    'a': PV.top(),
    'l': pv.list([PV.top(), pv.int(21), PV.top()]),
    'n': PV.top(),
    'm': PV.top(),
}
