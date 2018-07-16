from numpy import *
a = array([1,2,7])
a.var() # normalised with N (not N-1)
# 6.8888888888888875
a = array([[1,2,7],[4,9,6]])
a.var()
# 7.8055555555555571
a.var(axis=0) # the variance of each of the 3 columns
# array([ 2.25, 12.25, 0.25])
a.var(axis=1) # the variance of each of the 2 rows
# array([ 6.88888889, 4.22222222])

