from numpy import *
a = array([10,20])
tile(a, (3,2)) # concatenate 3x2 copies of a together
# array([[10, 20, 10, 20],
#        [10, 20, 10, 20],
#        [10, 20, 10, 20]])
tile(42.0, (3,2)) # works for scalars, too
# array([[ 42., 42.],
#        [ 42., 42.],
#        [ 42., 42.]])
tile([[1,2],[4,8]], (2,3)) # works for 2-d arrays and list literals, too
# array([[1, 2, 1, 2, 1, 2],
#        [4, 8, 4, 8, 4, 8],
#        [1, 2, 1, 2, 1, 2],
#        [4, 8, 4, 8, 4, 8]])

