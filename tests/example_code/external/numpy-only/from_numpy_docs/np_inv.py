from numpy import *
from numpy.linalg import inv
a = array([[3,1,5],[1,0,8],[2,1,4]])
print(a)
# [[3 1 5]
#  [1 0 8]
#  [2 1 4]]
inva = inv(a) # Inverse matrix
print(inva)
# [[ 1.14285714 -0.14285714 -1.14285714]
#  [-1.71428571 -0.28571429 2.71428571]
#  [-0.14285714 0.14285714 0.14285714]]
dot(a,inva) # Check the result, should be eye(3) within machine precision
# array([[ 1.00000000e-00, 2.77555756e-17, 3.60822483e-16],
#        [ 0.00000000e+00, 1.00000000e+00, 0.00000000e+00],
#        [ -1.11022302e-16, 0.00000000e+00, 1.00000000e+00]])

