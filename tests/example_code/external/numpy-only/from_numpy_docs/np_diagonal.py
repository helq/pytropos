from numpy import *
a = arange(12).reshape(3,4)
print(a)
# [[ 0 1 2 3]
#  [ 4 5 6 7]
#  [ 8 9 10 11]]
a.diagonal()
# array([ 0, 5, 10])
a.diagonal(offset=1)
# array([ 1, 6, 11])
diagonal(a) # Also this form exists
# array([ 0, 5, 10])

