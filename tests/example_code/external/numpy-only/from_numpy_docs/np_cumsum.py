from numpy import *
a = array([1,2,3]) # cumulative sum = intermediate summing results & total sum
a.cumsum()
# array([1, 3, 6])
cumsum(a) # also exists
# array([1, 3, 6])
a = array([[1,2,3],[4,5,6]])
a.cumsum(dtype=float) # specifies type of output value(s)
# array([ 1., 3., 6., 10., 15., 21.])
a.cumsum(axis=0) # sum over rows for each of the 3 columns
# array([[1, 2, 3],
#        [5, 7, 9]])
a.cumsum(axis=1) # sum over columns for each of the 2 rows
# array([[ 1, 3, 6],
#        [ 4, 9, 15]])

