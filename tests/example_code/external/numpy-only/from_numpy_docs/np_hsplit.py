from numpy import *
a = array([[1,2,3,4],[5,6,7,8]])
hsplit(a,2) # split, column-wise, in 2 equal parts
# [array([[1, 2],
#        [5, 6]]), array([[3, 4],
#        [7, 8]])]
hsplit(a,[1,2]) # split before column 1 and before column 2
# [array([[1],
#        [5]]), array([[2],
#        [6]]), array([[3, 4],
#        [7, 8]])]

