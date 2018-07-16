from numpy import *
a = array([1,2,3])
a.prod() # 1 * 2 * 3 = 6
# 6
prod(a) # also exists
# 6
a = array([[1,2,3],[4,5,6]])
a.prod(dtype=float) # specify type of output
# 720.0
a.prod(axis=0) # for each of the 3 columns: product
# array([ 4, 10, 18])
a.prod(axis=1) # for each of the two rows: product
# array([ 6, 120])

