import pytropos.internals.values as pv
from pytropos.internals.values.builtin_values import *
from pytropos.internals.values.python_values.builtin_mutvalues import *
from pytropos.internals.values.python_values.wrappers import *
from pytropos.internals.values.python_values.python_values import PythonValue, PT
from pytropos.libs_checking.numpy import *

exitcode = 1

def ndarray_(*lst):
    return PythonValue(NdArray(pv.tuple(*(pv.int(i) for i in lst))))

def list_int(*lst):
    return pv.list([pv.int(i) for i in lst])

store = {
  'np': numpy_module,
  'lst': pv.list([list_int(1, 3, 4), list_int(2, 8, 9)]),
  'a': pv.int(6),
  'a_': pv.int(6),
  'b': pv.tuple(pv.int(2), pv.int(3)),
  'b_': pv.tuple(pv.int(2), pv.int(3)),
  'c': pv.int(2),
  'c_': pv.int(2),
  'd': pv.Top,
  'd_': pv.Top,
}
