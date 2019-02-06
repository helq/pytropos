import pytropos.internals.values as pv
from pytropos.internals.values.builtin_values import *
from pytropos.internals.values.python_values.builtin_mutvalues import *
from pytropos.internals.values.python_values.wrappers import *
from pytropos.internals.values.python_values.python_values import PythonValue, PT
from pytropos.libs_checking.numpy import *

exitcode = 1

def ndarray_(*lst):
    return PythonValue(NdArray(pv.tuple(*(pv.int(i) for i in lst))))

store = {
  'zeros': PythonValue(zeros),
  'ones': PythonValue(ones),
  'Top': pv.Top,
  'NdArray': PythonValue(NdArrayAnnotation()),
  'a': PythonValue(NdArray.top()),
  'b': ndarray_(),
  'c': ndarray_(None),
  'd': ndarray_(None),
  'f': PythonValue(NdArray.top()),
  'g': PythonValue(NdArray.top()),
  'h': ndarray_(12, 1),
  'i': ndarray_(1, 2),
  'j': ndarray_(2, 3),
  'k': PythonValue(NdArray.top()),
  'l': ndarray_(2, 3, 1, 6),
  'm': PythonValue(NdArray.top()),
  'n': ndarray_(3, 5, 6, 2),
  'o': ndarray_(6, 2),
  'p': ndarray_(5, 1, 7, 6, 2),
  'q': PythonValue(NdArray.top()),
}

