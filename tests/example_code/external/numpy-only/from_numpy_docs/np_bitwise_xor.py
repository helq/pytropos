from numpy import *
bitwise_xor(array([2,5,255]), array([4,4,4]))
# array([ 6, 1, 251])
bitwise_xor(array([2,5,255,2147483647],dtype=int32), array([4,4,4,2147483647],dtype=int32))
# array([ 6, 1, 251, 0])

