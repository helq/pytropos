from numpy import *
m = matrix('1 2; 5 8')
m
# matrix([[1, 2],
#        [5, 8]])
a = asarray(m) # a is array type with same contents as m -- data is not copied
a
# array([[1, 2],
#        [5, 8]])
m[0,0] = -99
m
# matrix([[-99, 2],
#        [ 5, 8]])
a # no copy was made, so modifying m modifies a, and vice versa
# array([[-99, 2],
#        [ 5, 8]])

