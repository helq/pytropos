from math import inf
import pytropos.internals.values as pv
from pytropos.internals.values.builtin_values import *
from pytropos.internals.values.python_values.builtin_mutvalues import *
from pytropos.internals.values.python_values.wrappers import *
from pytropos.internals.values.python_values.python_values import PythonValue, PT
from pytropos.libs_checking.numpy import *

exitcode = 1

store = {
  'np': numpy_module,
  'm': pv.Top,
  'n': pv.Top,
  '_': pv.tuple(),
  '__': pv.tuple(pv.int(1)),
  'a': pv.tuple(pv.int(2)),
  'b_': PythonValue(NdArray(pv.tuple(pv.int(2), pv.int(3)))),
  'b': pv.tuple(pv.int(2), pv.int(3)),
  'c': pv.tuple(pv.int(2)),
  'd': pv.tuple(pv.int(2), pv.int(3)),
  # TODO(helq): fix np.array, 'e' should be the commented tuple below
  # 'e': PythonValue(Tuple([pv.int(2)], size=(1,3))),  # THIS IS THE RIGHT ANSWER
  'e': PythonValue(Tuple([pv.int(2)], size=(1,inf))),
  'f': pv.tuple(pv.int(3)),
  'g': PythonValue(Tuple([pv.int(2)], size=(1,inf))),
  'ls': pv.list([pv.list([pv.int(i) for i in [1, 2, 3, 4, 5]]), pv.list([pv.int(i) for i in [3, 4, 0, 0, 1]])]),
  'h': pv.tuple(pv.int(3), pv.int(2), pv.int(5)),
  'i': PythonValue(Tuple([pv.int(3)], size=(1,inf))),
  'j': PythonValue(Tuple([pv.int(3)], size=(1,inf))),
  'k': PythonValue(Tuple([pv.int(1), pv.int(3)], size=(2,inf))),
  'l': pv.tuple(pv.int(2), pv.int(3)),
}
