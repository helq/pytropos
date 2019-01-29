import pytropos.internals.values as pv
from pytropos.internals.values.builtin_values import *
from pytropos.internals.values.python_values.builtin_mutvalues import *
from pytropos.internals.values.python_values.wrappers import *
from pytropos.internals.values.python_values.python_values import PythonValue, PT
from pytropos.libs_checking.numpy import NdArray

exitcode = 1

store = {
  'np': PythonValue(BuiltinModule('numpy', funcs={'ndarray': BuiltinClass('ndarray', klass=NdArray, args=[(Tuple, Int, List)], kargs={})}, read_only=False)),
  'nonexistent': PythonValue(BuiltinModule()),
  'a': PythonValue(NdArray(pv.tuple(pv.int(2), pv.int()))),
  'b': pv.Top,
  'c': pv.Top,
  'd': PythonValue(NdArray(pv.tuple())),
  'e': pv.Top,
  'f': PythonValue(NdArray(pv.tuple(pv.int(2), pv.int()))),
}
