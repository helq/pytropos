from numpy import *
a =array([[1],[2]]) # 2x1 array
b = array([[3,4],[5,6]]) # 2x2 array
hstack((a,b,a)) # only the 2nd dimension of the arrays is allowed to be different
# array([[1, 3, 4, 1],
#        [2, 5, 6, 2]])

