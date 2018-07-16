from numpy import *
a = arange(12).reshape(4,3)
a
# array([[ 0, 1, 2],
#        [ 3, 4, 5],
#        [ 6, 7, 8],
#        [ 9, 10, 11]])
rot90(a) # 'rotate' the matrix 90 degrees
# array([[ 2, 5, 8, 11],
#        [ 1, 4, 7, 10],
#        [ 0, 3, 6, 9]])

