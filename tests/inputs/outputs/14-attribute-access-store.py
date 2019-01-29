from pytropos.internals.values.builtin_values import *
from pytropos.internals.values.python_values.builtin_mutvalues import *
from pytropos.internals.values.python_values import PythonValue

exitcode = 1

store = {
  'a': PythonValue(List([PythonValue(Int(2)), PythonValue(Int(6))], size=(2,2))),
  'dd': PythonValue(NoneType())
}
