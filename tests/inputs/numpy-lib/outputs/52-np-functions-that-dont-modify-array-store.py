import pytropos.internals.values as pv
from pytropos.internals.values.builtin_values import *
from pytropos.internals.values.python_values.builtin_mutvalues import *
from pytropos.internals.values.python_values.wrappers import *
from pytropos.internals.values.python_values.python_values import PythonValue, PT
from pytropos.libs_checking.numpy import *

exitcode = 0

def ndarray_(*lst):
    return PythonValue(NdArray(pv.tuple(*(pv.int(i) for i in lst))))

shape = ndarray_(2, 6, 7, 3)

store = {
  'np': numpy_module,
  'a': shape,
  'copy01': shape,
  'copy02': shape,
  'copy03': shape,
  'copy04': shape,
  'copy05': shape,
  'copy06': shape,
  'copy07': shape,
  'copy08': shape,
  'copy09': shape,
  'copy10': shape,
}
