from numpy import *
a = array([[1,2],[5,8]])
a
# array([[1, 2],
#        [5, 8]])
m = asmatrix(a) # m is matrix type with same contents as a -- data is not copied
m
# matrix([[1, 2],
#        [5, 8]])
a[0,0] = -99
a
# array([[-99, 2],
#        [ 5, 8]])
m # no copy was made so modifying a modifies m, and vice versa
# matrix([[-99, 2],
#        [ 5, 8]])

