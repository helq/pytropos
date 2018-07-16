from numpy import *
a = arange(9).reshape(3,3)
print(a)
# [[0 1 2]
#  [3 4 5]
#  [6 7 8]]
indices = ix_([0,1,2],[1,2,0]) # trick to be used with array broadcasting
print(indices)
# (array([[0],
#        [1],
#        [2]]), array([[1, 2, 0]]))
print((a[indices]))
# [[1 2 0]
#  [4 5 3]
#  [7 8 6]]
# The latter array is the cross-product:
# [[ a[0,1] a[0,2] a[0,0]]
    # [ a[1,1] a[1,2] a[1,0]]
    # [ a[2,1] a[2,2] a[2,0]]]
# ...

