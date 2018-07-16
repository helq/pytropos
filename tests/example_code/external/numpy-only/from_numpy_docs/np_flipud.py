from numpy import *
a = arange(12).reshape(4,3)
a
# array([[ 0, 1, 2],
#        [ 3, 4, 5],
#        [ 6, 7, 8],
#        [ 9, 10, 11]])
flipud(a) # flip up-down
# array([[ 9, 10, 11],
#        [ 6, 7, 8],
#        [ 3, 4, 5],
#        [ 0, 1, 2]])

