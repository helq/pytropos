from numpy import *
from numpy.linalg import svd
A = array([[1., 3., 5.],[2., 4., 6.]]) # A is a (2x3) matrix
U,sigma,V = svd(A)
print(U) # U is a (2x2) unitary matrix
# [[-0.61962948 -0.78489445]
#  [-0.78489445 0.61962948]]
print(sigma) # non-zero diagonal elements of Sigma
# [ 9.52551809 0.51430058]
print(V) # V is a (3x3) unitary matrix
# [[-0.2298477 -0.52474482 -0.81964194]
#  [ 0.88346102 0.24078249 -0.40189603]
#  [ 0.40824829 -0.81649658 0.40824829]]
Sigma = zeros_like(A) # constructing Sigma from sigma
n = min(A.shape)
Sigma[:n,:n] = diag(sigma)
print((dot(U,dot(Sigma,V)))) # A = U * Sigma * V
# [[ 1. 3. 5.]
#  [ 2. 4. 6.]]

