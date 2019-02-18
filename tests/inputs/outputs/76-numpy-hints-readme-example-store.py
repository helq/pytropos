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
  'data': pv.Top,
  'NdArray': PythonValue(NdArrayAnnotation()),
  'A': ndarray_(2, 3),
  'x': ndarray_(4),
  'y': PythonValue(NdArray.top()),
}
