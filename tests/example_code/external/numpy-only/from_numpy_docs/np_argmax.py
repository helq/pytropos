from numpy import *
a = array([10,20,30])
maxindex = a.argmax()
a[maxindex]
# 30
a = array([[10,50,30],[60,20,40]])
maxindex = a.argmax()
maxindex
# 3
a.ravel()[maxindex]
# 60
a.argmax(axis=0) # for each column: the row index of the maximum value
# array([1, 0, 1])
a.argmax(axis=1) # for each row: the column index of the maximum value
# array([1, 0])
argmax(a) # also exists, slower, default is axis=-1
# array([1, 0])

