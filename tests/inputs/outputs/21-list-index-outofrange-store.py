import pytropos.internals.values as pv
from pytropos.internals.values.builtin_values import *
from pytropos.internals.values.python_values.builtin_mutvalues import *
from pytropos.internals.values.python_values.wrappers import *
from pytropos.internals.values.python_values.python_values import PythonValue, PT

exitcode = 1

store = {
  'a': pv.list([pv.int(2), pv.float(3.0), pv.tuple()]),
}
