from numpy import *
a = arange(12).reshape(3,4)
a
# array([[ 0, 1, 2, 3],
#        [ 4, 5, 6, 7],
#        [ 8, 9, 10, 11]])
a.diagonal()
# array([ 0, 5, 10])
a.trace()
# 15
a.diagonal(offset=1)
# array([ 1, 6, 11])
a.trace(offset=1)
# 18

