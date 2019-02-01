import pytropos.internals.values as pv
from pytropos.internals.values.builtin_values import *
from pytropos.internals.values.python_values.builtin_mutvalues import *
from pytropos.internals.values.python_values.wrappers import *
from pytropos.internals.values.python_values.python_values import PythonValue, PT
from pytropos.libs_checking.numpy import *

exitcode = 1

def to_pv_Tuple(*ints):
    return pv.tuple(*(pv.int(i) for i in ints))

store = {
  'np': numpy_module,
  'a': to_pv_Tuple(2, 3, 4),
  'b': pv.Top,
  'c': to_pv_Tuple(2, 2, 4),
  'd': to_pv_Tuple(7, 1, 8),
  'e': pv.Top,
  'f': to_pv_Tuple(5, 3, 1),

   # This shouldn't exists, with more precise NdArrays should be possible to dectect that
   # lists cannot be `mod` to floats
  'g': to_pv_Tuple(5, 1, 3),

  'h': to_pv_Tuple(5, 1, 3),
}
