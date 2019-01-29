import pytropos.internals.values as pv
from pytropos.internals.values.builtin_values import *
from pytropos.internals.values.python_values.builtin_mutvalues import *
from pytropos.internals.values.python_values.wrappers import *
from pytropos.internals.values.python_values.python_values import PythonValue, PT

exitcode = 1

r = PythonValue(List([pv.int(21)], size=(1, 1)))

store = {
  '_': PythonValue(PT.Top),
  'f': r.val.children[('attr', 'append')],
  'r': r,
}
