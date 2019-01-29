import pytropos.internals.values as pv
from pytropos.internals.values.builtin_values import *
from pytropos.internals.values.python_values.builtin_mutvalues import *
from pytropos.internals.values.python_values.wrappers import *
from pytropos.internals.values.python_values.python_values import PythonValue, PT
from pytropos.libs_checking.numpy import NdArray

exitcode = 1

store = {
  'np': PythonValue(BuiltinModule('numpy', funcs={'ndarray': BuiltinClass('ndarray', klass=NdArray, args=[(Tuple, Int, List)], kargs={})}, read_only=False)),
  'c': pv.Top,
  '_': pv.Top,
  'a': PythonValue(NdArray(pv.tuple(pv.int(2), pv.int()))),
  'nonexistent': PythonValue(BuiltinModule()),
  'b': PythonValue(Tuple((pv.int(2), pv.int()), size=(2,2))),
}
