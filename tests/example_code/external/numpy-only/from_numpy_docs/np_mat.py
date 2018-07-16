from numpy import *
mat('1 3 4; 5 6 9') # matrices are always 2-dimensional
# matrix([[1, 3, 4],
#        [5, 6, 9]])
a = array([[1,2],[3,4]])
m = mat(a) # convert 2-d array to matrix
m
# matrix([[1, 2],
#        [3, 4]])
a[0] # result is 1-dimensional
# array([1, 2])
m[0] # result is 2-dimensional
# matrix([[1, 2]])
a.ravel() # result is 1-dimensional
# array([1, 2, 3, 4])
m.ravel() # result is 2-dimensional
# matrix([[1, 2, 3, 4]])
a*a # element-by-element multiplication
# array([[ 1, 4],
#        [ 9, 16]])
m*m # (algebraic) matrix multiplication
# matrix([[ 7, 10],
#        [15, 22]])
a**3 # element-wise power
# array([[ 1, 8],
#        [27, 64]])
m**3 # matrix multiplication m*m*m
# matrix([[ 37, 54],
#        [ 81, 118]])
m.T # transpose of the matrix
# matrix([[1, 3],
#        [2, 4]])
m.H # conjugate transpose (differs from .T for complex matrices)
# matrix([[1, 3],
#        [2, 4]])
m.I # inverse matrix
# matrix([[-2. , 1. ],
#        [ 1.5, -0.5]])

