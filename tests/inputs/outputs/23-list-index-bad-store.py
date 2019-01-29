import pytropos.internals.values as pv
from pytropos.internals.values.builtin_values import *
from pytropos.internals.values.python_values.builtin_mutvalues import *
from pytropos.internals.values.python_values.wrappers import *
from pytropos.internals.values.python_values.python_values import PythonValue, PT

exitcode = 0

l = [pv.int(i) for i in range(10)]

store = {
  'p': pv.list(l),
  'i': pv.int(10),
}
