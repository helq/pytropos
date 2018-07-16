from numpy import *
a = array([1,2,3])
a.sum()
# 6
sum(a) # also exists
a = array([[1,2,3],[4,5,6]])
a.sum()
# 21
a.sum(dtype=float) # specify type of output
# 21.0
a.sum(axis=0) # sum over rows for each of the 3 columns
# array([5, 7, 9])
a.sum(axis=1) # sum over columns for each of the 2 rows
# array([ 6, 15])

