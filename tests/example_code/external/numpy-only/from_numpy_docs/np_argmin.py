from numpy import *
a = array([10,20,30])
minindex = a.argmin()
a[minindex]
# 10
a = array([[10,50,30],[60,20,40]])
minindex = a.argmin()
minindex
# 0
a.ravel()[minindex]
# 10
a.argmin(axis=0) # for each column: the row index of the minimum value
# array([0, 1, 0])
a.argmin(axis=1) # for each row: the column index of the minimum value
# array([0, 1])
argmin(a) # also exists, slower, default is axis=-1
# array([0, 1])

