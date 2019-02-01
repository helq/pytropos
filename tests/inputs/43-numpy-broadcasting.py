import numpy as np

a = (np.zeros(  (2, 1, 4)) + np.zeros(    (3,1)) ).shape  # must be (2, 3, 4)
b = (np.zeros(  (2, 2, 4)) + np.zeros(    (3,1)) ).shape  # broadcasting error
c = (np.zeros(  (2, 2, 4)) - 3                   ).shape  # must be (2, 2, 4)
d = (np.zeros(  (7, 1, 8)) / [7]                 ).shape  # must be (7, 1, 8)
e = (np.zeros(  (2, 2, 4)) * [7,3]               ).shape  # broadcasting error
f = (        ([2],[3],[6]) % np.ndarray( (5,1,1))).shape  # must be (5, 3, 1)

# The following is a very comple example that doesn't work when run in python but it does
# work in Pytropos
# This should fail because mod operation cannot be done over lists (the left operand has
# lists no floating numbers as values. (It gets converted from tuple to np.array when
# operated with a np.array)).
g = (      ([2],[3],[6,0]) % np.ndarray( (5,1,1))).shape  # Pytropos says (5, 1, 3)
h = (np.zeros(  (3,))      + np.zeros(   (5,1,1))).shape  # must be (5, 1, 3)

# show_store()
