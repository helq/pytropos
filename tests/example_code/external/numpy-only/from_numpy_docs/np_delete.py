from numpy import *
a = array([0, 10, 20, 30, 40])
delete(a, [2,4]) # remove a[2] and a[4]
# array([ 0, 10, 30])
a = arange(16).reshape(4,4)
a
# array([[ 0, 1, 2, 3],
#        [ 4, 5, 6, 7],
#        [ 8, 9, 10, 11],
#        [12, 13, 14, 15]])
delete(a, s_[1:3], axis=0) # remove rows 1 and 2
# array([[ 0, 1, 2, 3],
#        [12, 13, 14, 15]])
delete(a, s_[1:3], axis=1) # remove columns 1 and 2
# array([[ 0, 3],
#        [ 4, 7],
#        [ 8, 11],
#        [12, 15]])

