from numpy import *
a = array([1,2,3,4])
a.resize(2,2) # changes shape of 'a' itself
print(a)
# [[1 2]
#  [3 4]]
a.resize(3,2) # reallocates memoy of 'a' to change nr of elements, fills excess elements with 0
print(a)
# [[1 2]
#  [3 4]
#  [0 0]]
a.resize(2,4)
print(a)
# [[1 2 3 4]
#  [0 0 0 0]]
a.resize(2,1) # throws away elements of 'a' to fit new shape
print(a)
# [[1]
#  [2]]

