import pytropos.internals.values as pv
from pytropos.internals.values.builtin_values import *
from pytropos.internals.values.python_values.builtin_mutvalues import *
from pytropos.internals.values.python_values.wrappers import *
from pytropos.internals.values.python_values.python_values import PythonValue, PT
from pytropos.libs_checking.numpy import *

exitcode = 0

store = {
  'np': numpy_module,
  'a': PythonValue(NdArray(pv.tuple(pv.int(1)))),
  'b': PythonValue(NdArray(pv.tuple(pv.int(2), pv.int(2)))),
  'c': PythonValue(NdArray(pv.tuple(pv.int(2), pv.int(2)))),
}
