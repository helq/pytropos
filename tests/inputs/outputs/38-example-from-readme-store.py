import pytropos.internals.values as pv
from pytropos.internals.values.builtin_values import *
from pytropos.internals.values.python_values.builtin_mutvalues import *
from pytropos.internals.values.python_values.wrappers import *
from pytropos.internals.values.python_values.python_values import PythonValue, PT
from pytropos.libs_checking.numpy import *

exitcode = 1

def ndarray_(*lst):
    return PythonValue(NdArray(pv.tuple(*(pv.int(i) for i in lst))))

store = {
  'np': numpy_module,
  'a': ndarray_(10, 6),
  'm': pv.int(4),
  'n': pv.int(2),
  'b': ndarray_(3, 11),
  'res': PythonValue(NdArray.top()),
  'var': pv.bool(True),
}
