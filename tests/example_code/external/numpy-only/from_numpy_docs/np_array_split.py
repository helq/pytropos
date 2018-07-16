from numpy import *
a = array([[1,2,3,4],[5,6,7,8]])
array_split(a,2,axis=0) # split a in 2 parts. row-wise
# [array([[1, 2, 3, 4]]), array([[5, 6, 7, 8]])]
array_split(a,4,axis=1) # split a in 4 parts, column-wise
# [array([[1],
#        [5]]), array([[2],
#        [6]]), array([[3],
#        [7]]), array([[4],
#        [8]])]
#  array_split(a,3,axis=1) # impossible to split in 3 equal parts -> first part(s) are bigger
# [array([[1, 2],
#        [5, 6]]), array([[3],
#        [7]]), array([[4],
#        [8]])]
array_split(a,[2,3],axis=1) # make a split before the 2nd and the 3rd column
# [array([[1, 2],
#        [5, 6]]), array([[3],
#        [7]]), array([[4],
#        [8]])]

