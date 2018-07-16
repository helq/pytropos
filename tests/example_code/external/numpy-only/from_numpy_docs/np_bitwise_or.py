from numpy import *
bitwise_or(array([2,5,255]), array([4,4,4]))
# array([ 6, 5, 255])
bitwise_or(array([2,5,255,2147483647],dtype=int32), array([4,4,4,2147483647],dtype=int32))
# array([ 6, 5, 255, 2147483647])

