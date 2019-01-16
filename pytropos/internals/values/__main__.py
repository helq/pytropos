from .python_values import PythonValue
from .builtin_mutvalues import List
from .builtin_values import NoneType
from ..errors import TypeCheckLogger

from .__init__ import int, float, bool, none, list

print("Testing Python Values")

val1 = PythonValue.top()
val2 = int()
val3 = int(2)
val4 = int(3)
print(f"{val1} + {val2} == {val1.add(val2)}")
print(f"{val1} + {val3} == {val1.add(val3)}")
print(f"{val2} + {val3} == {val2.add(val3)}")
print(f"{val3} + {val4} == {val3.add(val4)}")
print(f"{val3} * {val4} == {val3.mul(val4)}")

val2 = float()
val3 = float(0.0)
val4 = float(3.0)
val5 = val3.floordiv(val3)
print(f"{val1} + {val2} == {val1.add(val2)}")
print(f"{val1} + {val3} == {val1.add(val3)}")
print(f"{val2} + {val3} == {val2.add(val3)}")
print(f"{val3} + {val4} == {val3.add(val4)}")
print(f"{val3} * {val4} == {val3.mul(val4)}")
print(f"{val3} / {val3} == {val3.truediv(val3)}")
print(f"{val3} // {val3} == {val5}")
print(f"{val5}.is_top() == {val5.is_top()}")

val1 = int(0)
val2 = float(1.0)
print(f"{val1} / {val2} == {val1.truediv(val2)}")

val1 = bool(True)
val2 = int()
print(f"{val1} + {val2} == {val1.add(val2)}")

val1 = bool(True)
val2 = bool(True)
print(f"{val1} + {val2} == {val1.add(val2)}")

val1 = bool(True)
val2 = int()
print(f"{val1} << {val2} == {val1.lshift(val2)}")

val1 = none()
val2 = int(3)
print(f"{val1} << {val2} == {val1.lshift(val2)}")

print(f"NoneType() is NoneType() == {NoneType() is NoneType()}")
print(f"none() is none() == {none() is none()}")

print(f"Errors: {TypeCheckLogger()}")

# Using List as arbitrary python objects
# val1 = PythonValue(List(children={'size': int(2)}))
# val2 = PythonValue(List(children={'size': int(3)}))

# print(val1)
# print(val2)

# val3 = val1.join_mut(val2, {})

# print(val3)
# print()

# # What if we add recursion?
# val1 = PythonValue(List(children={'size': int(3)}))
# val2 = PythonValue(List(children={'size': int(2)}))

# val1.val.children['me'] = val1  # type: ignore
# val2.val.children['me'] = val2  # type: ignore

# print(val1)
# print(val2)

# val3 = val1.join_mut(val2, {})

# print(val3)
print()

# Using other lists
val1 = list([int(3), list([int(6)])])
val2 = list([int(5)])

val2.val.children[('index', 1)] = val2
val2.val.size = (2, 2)

# In plain python:
# val1 = [3, [6]]
# val2 = [5]
# val2.append(val2)

print(f"val1 = {val1}")
print(f"val2 = {val2}")

val3 = val1.join_mut(val2, {})

print(f"val1.join(val2) => {val3}")
print()

# Using other lists
val1 = list([int(3), list([int(6)])])
val2 = list([int(5), list([])])

val2.val.children[('index', 1)].val.children[('index', 0)] = val2.val.children[('index', 1)]
val2.val.children[('index', 1)].val.size = (1, 1)

# In plain python:
# val1 = [3, [6]]
# val2 = [5, []]
# val2[1].append(val2)

print(f"val1 = {val1}")
print(f"val2 = {val2}")

val3 = val1.join_mut(val2, {})

print(f"val1.join(val2) => {val3}")
print()

# Using other lists
val1 = list([int(3), list([])])
val2 = list([int(5), list([])])

val1.val.children[('index', 1)].val.children[('index', 0)] = val1.val.children[('index', 1)]  # type: ignore  # noqa: E501
val1.val.children[('index', 1)].val.size = (1, 1)  # type: ignore  # noqa: E501

val2.val.children[('index', 1)].val.children[('index', 0)] = val2.val.children[('index', 1)]
val2.val.children[('index', 1)].val.size = (1, 1)

# In plain python:
# val1 = [3, []]
# val1[1].append(val1)
# val2 = [5, []]
# val2[1].append(val2)

print(f"val1 = {val1}")
print(f"val2 = {val2}")

val3 = val1.join_mut(val2, {})

print(f"val1.join(val2) => {val3}")
print()

# Using other lists
val1 = list([int(3), list([])])
val2 = list([int(5), list([])])

val1.val.children[('index', 1)].val.children[('index', 0)] = val1.val.children[('index', 1)]  # type: ignore  # noqa: E501
val1.val.children[('index', 1)].val.size = (1, 1)  # type: ignore  # noqa: E501
val1.val.children[('index', 0)] = val1.val.children[('index', 1)]  # type: ignore  # noqa: E501

val2.val.children[('index', 1)].val.children[('index', 0)] = val2.val.children[('index', 1)]
val2.val.children[('index', 1)].val.size = (1, 1)

# In plain python:
# val1 = [3, []]
# val1[1].append(val1)
# val1[0] = val1[1]
# val2 = [5, []]
# val2[1].append(val2)

print(f"val1 = {val1}")
print(f"val2 = {val2}")

val3 = val1.join_mut(val2, {})

print(f"val1.join(val2) => {val3}")
print()

# Using other lists
val1 = list([int(3), list([]), int(2)])
val2 = list([int(5), list([])])

print(f"val1 = {val1}")
print(f"val2 = {val2}")

val3 = val1.join_mut(val2, {})

print(f"val1.join(val2) => {val3}")
print()

# Using other lists
val1 = list([list(), list([]), int(2)])
val2 = list([list([]), list([])])

print(f"val1 = {val1}")
print(f"val2 = {val2}")

val3 = val1.join_mut(val2, {})

print(f"val1.join(val2) => {val3}")
print()

# Using other lists
val1 = list([list([list([int(5)])]), list([])])
val2 = list([list([list([int(5)])])])

val2.val.children[('index', 1)] = val2.val.children[('index', 0)].val.children[('index', 0)]
val2.val.size = (2, 2)

# In plain python:
# val1 = [[[5]], []]
# val2 = [[[5]]]
# val2.append(val2[0][0])

print(f"val1 = {val1}")
print(f"val2 = {val2}")

val3 = val1.join_mut(val2, {})

print(f"val1.join(val2) => {val3}")
print()

# Using other lists
val1 = list([PythonValue.top(), PythonValue(List.top())])
val2 = list([int(2), list([list([int(5)])])])

print(f"val1 = {val1}")
print(f"val2 = {val2}")

val3 = val1.join_mut(val2, {})

print(f"val1.join(val2) => {val3}")
print()
