from numpy import *
a = array([[[1,2]],[[3,4]]])
print(a)
# [[[1 2]]
#  [[3 4]]]
b = a.flatten() # b is now a 1-d version of a, a new array, not a reference
print(b)
# [1 2 3 4]

