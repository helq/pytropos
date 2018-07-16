from numpy import *
a = array([3,5,7,9])
b = array([10,20,30,40])
c = array([2,4,6,8])
where(a <= 6, b, c)
# array([10, 20, 6, 8])
where(a <= 6, b, -1)
# array([10, 20, -1, -1])
indices = where(a <= 6) # returns a tuple; the array contains indices.
indices
# (array([0, 1]),)
b[indices]
# array([10, 20])
b[a <= 6] # an alternative syntax
# array([10, 20])
d = array([[3,5,7,9],[2,4,6,8]])
where(d <= 6) # tuple with first all the row indices, then all the column indices
# (array([0, 0, 1, 1, 1]), array([0, 1, 0, 1, 2]))

