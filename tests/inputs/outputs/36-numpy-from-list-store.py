import pytropos.internals.values as pv
from pytropos.internals.values.builtin_values import *
from pytropos.internals.values.python_values.builtin_mutvalues import *
from pytropos.internals.values.python_values.wrappers import *
from pytropos.internals.values.python_values.python_values import PythonValue, PT
from pytropos.libs_checking.numpy import *

exitcode = 0

shape_l = pv.list([pv.int(i) for i in (2, 5, 8, 11, 14, 17, 20, 23, 26, 29)])
shape = pv.tuple(*[pv.int(i) for i in (2, 5, 8, 11, 14, 17, 20, 23, 26, 29)])

store = {
  'np': numpy_module,
  'shape': shape_l,
  'i': pv.int(10),
  'newarray': PythonValue(NdArray(shape)),
}
