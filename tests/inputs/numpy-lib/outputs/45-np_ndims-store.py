import pytropos.internals.values as pv
from pytropos.internals.values.builtin_values import *
from pytropos.internals.values.python_values.builtin_mutvalues import *
from pytropos.internals.values.python_values.wrappers import *
from pytropos.internals.values.python_values.python_values import PythonValue, PT
from pytropos.libs_checking.numpy import *

exitcode = 0

store = {
  'array': PythonValue(array),
  'zeros': PythonValue(zeros),
  'x': PythonValue(NdArray(pv.tuple(pv.int(3)))),
  'y': PythonValue(NdArray(pv.tuple(pv.int(2), pv.int(3), pv.int(4)))),
  'xn': pv.int(1),
  'yn': pv.int(3),
}
