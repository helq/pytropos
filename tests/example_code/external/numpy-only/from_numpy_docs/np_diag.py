from numpy import *
a = arange(12).reshape(4,3)
print(a)
# [[ 0 1 2]
#  [ 3 4 5]
#  [ 6 7 8]
#  [ 9 10 11]]
print((diag(a,k=0)))
# [0 4 8]
print((diag(a,k=1)))
# [1 5]
print((diag(array([1,4,5]),k=0)))
# [[1 0 0]
#  [0 4 0]
#  [0 0 5]]
print((diag(array([1,4,5]),k=1)))
# [[0 1 0 0]
#  [0 0 4 0]
#  [0 0 0 5]
#  [0 0 0 0]]

