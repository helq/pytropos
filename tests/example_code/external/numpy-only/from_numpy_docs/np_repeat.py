from numpy import *
repeat(7., 4)
# array([ 7., 7., 7., 7.])
a = array([10,20])
a.repeat([3,2])
# array([10, 10, 10, 20, 20])
repeat(a, [3,2]) # also exists
a = array([[10,20],[30,40]])
a.repeat([3,2,1,1])
# array([10, 10, 10, 20, 20, 30, 40])
a.repeat([3,2],axis=0)
# array([[10, 20],
#        [10, 20],
#        [10, 20],
#        [30, 40],
#        [30, 40]])
a.repeat([3,2],axis=1)
# array([[10, 10, 10, 20, 20],
#        [30, 30, 30, 40, 40]])

