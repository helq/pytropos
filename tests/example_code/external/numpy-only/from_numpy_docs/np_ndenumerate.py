from numpy import *
a = arange(9).reshape(3,3) + 10
a
# array([[10, 11, 12],
#        [13, 14, 15],
#        [16, 17, 18]])
b = ndenumerate(a)
for position,value in b: print((position,value)) # position is the N-dimensional index
# ...
# (0, 0) 10
# (0, 1) 11
# (0, 2) 12
# (1, 0) 13
# (1, 1) 14
# (1, 2) 15
# (2, 0) 16
# (2, 1) 17
# (2, 2) 18

