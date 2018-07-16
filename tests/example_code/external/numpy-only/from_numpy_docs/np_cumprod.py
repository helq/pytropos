from numpy import *
a = array([1,2,3])
a.cumprod() # total product 1*2*3 = 6, and intermediate results 1, 1*2
# array([1, 2, 6])
cumprod(a) # also exists
# array([1, 2, 6])
a = array([[1,2,3],[4,5,6]])
a.cumprod(dtype=float) # specify type of output
# array([1., 2., 6., 24., 120., 720.])
a.cumprod(axis=0) # for each of the 3 columns: product and intermediate results
# array([[ 1, 2, 3],
#        [ 4, 10, 18]])
a.cumprod(axis=1) # for each of the two rows: product and intermediate results
# array([[ 1, 2, 6],
#        [ 4, 20, 120]])

