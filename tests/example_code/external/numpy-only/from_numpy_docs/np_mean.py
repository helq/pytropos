from numpy import *
a = array([1,2,7])
a.mean()
# 3.3333333333333335
a = array([[1,2,7],[4,9,6]])
a.mean()
# 4.833333333333333
a.mean(axis=0) # the mean of each of the 3 columns
# array([ 2.5, 5.5, 6.5])
a.mean(axis=1) # the mean of each of the 2 rows
# array([ 3.33333333, 6.33333333])

