import pytropos.internals.values as pv
from pytropos.internals.values.builtin_values import *
from pytropos.internals.values.python_values.builtin_mutvalues import *
from pytropos.internals.values.python_values.wrappers import *
from pytropos.internals.values.python_values.python_values import PythonValue, PT
from pytropos.libs_checking.numpy import NdArray

exitcode = 1

t = pv.tuple(pv.int(2), pv.int())

store = {
  'np': PythonValue(BuiltinModule('numpy', funcs={'ndarray': BuiltinClass('ndarray', klass=NdArray, args=[(Tuple, Int, List)], kargs={})}, read_only=False)),
  'nonexistent': PythonValue(BuiltinModule()),
  'a': PythonValue(NdArray(t)),
  'b': t,
  'c': pv.Top,
  '_': pv.Top,
}
