from numpy import *
bitwise_and(array([2,5,255]), array([4,4,4]))
# array([0, 4, 4])
bitwise_and(array([2,5,255,2147483647],dtype=int32), array([4,4,4,2147483647],dtype=int32))
# array([ 0, 4, 4, 2147483647])

