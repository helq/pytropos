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
  'somelib': pv.ModuleTop,
  'NdArray': PythonValue(NdArrayAnnotation()),
  'a': ndarray_(2, 3, 4),
  'b': ndarray_(1, 2),
  'c': ndarray_(2, 1),
  'd': ndarray_(2, 2),
  'e': ndarray_(2, 1),
  'f': ndarray_(),
  'g': ndarray_(None, 2),
  'h': ndarray_(6, 2),
  'i': ndarray_(10),
}
