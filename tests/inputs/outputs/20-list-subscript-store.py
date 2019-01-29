import pytropos.internals.values as pv
from pytropos.internals.values.builtin_values import *
from pytropos.internals.values.python_values.builtin_mutvalues import *
from pytropos.internals.values.python_values.wrappers import *
from pytropos.internals.values.python_values.python_values import PythonValue, PT

exitcode = 1

b_ = pv.list([pv.float(5.0), pv.none()])
a = pv.list([pv.int(9), b_])
b_.val.children['index', 1] = a

store = {
  'a': a,
  'b': a.val.children['attr', 'append'],
  'c': b_.val.children['attr', 'append'],
}
